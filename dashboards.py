import os
import argparse
import json
from library import utils
import library.clients.dbentityclient as dbclient
import library.clients.entityclient as entityclient
import library.localstore as store
import library.nrpylogger as nrpylogger

db_entity = dbclient.DashboardEntity()
ec = entityclient.EntityClient()
logger = nrpylogger.get_logger(os.path.basename(__file__))
NO_NAME = "NONE"


def setup_params(parser):
    parser.add_argument('--fromAccount', nargs=1, type=int, required=True, help='source accountId')
    parser.add_argument('--fromApiKey', nargs=1, type=str, required=True, help='fromAccount User API Key')
    parser.add_argument('--entityGuid', nargs=1, type=str, required=True, help='Dashboard entityGuid')
    parser.add_argument('--download', dest='download', required=False, action='store_true',
                        help='Download Dashboard JSON')
    parser.add_argument('--copy', dest='copy', required=False, action='store_true',
                        help='Copy Dashboard')
    parser.add_argument('--toAccount', nargs=1, type=int, required=False, help='target accountId')
    parser.add_argument('--toApiKey', nargs=1, type=str, required=False, help='toAccount User API Key. Optional in '
                                                                              'case fromApiKey works for both accounts ')
    parser.add_argument('--toName', nargs=1, type=str, required=False, help='name of copied dashboard')


def print_params():
    logger.info("fromAccount : " + str(args.fromAccount[0]))
    logger.info("fromApiKey : " + len(args.fromApiKey[:-4]) * "*" + args.fromApiKey[-4:])
    if args.entityGuid:
        logger.info("Dashboard entityGuid " + args.entityGuid[0])
    if args.download:
        logger.info("action : download")
    if args.copy:
        logger.info("action: copy ")
        logger.info("toAccount : " + str(args.toAccount[0]))
        if args.toApiKey:
            logger.info("toApiKey : " + len(args.toApiKey[:-4]) * "*" + args.toApiKey[-4:])
        else:
            logger.info("No toApiKey provided. Will use fromApiKey to copy to toAccount: ")
        if args.toName:
            logger.info("toName : " + args.toApiKey[0])
        else:
            logger.info("No toName provided. Will prefix existing name with Copy")


def download(per_api_key, entity_guid):
    result = db_entity.get(per_api_key, entity_guid)
    dashboard = result['response']['data']['actor']['entity']
    db_file_name = str(dashboard['accountId']) + "-" + dashboard['name'] + ".json"
    store.save_json_to_file(dashboard, db_file_name)


def copy_dashboard(per_api_key, entity_guid, to_acct, to_api_key, to_name):
    result = db_entity.get(per_api_key, entity_guid)
    dashboard = result['response']['data']['actor']['entity']
    if to_name == NO_NAME:
        to_name = "Copy of " + dashboard["name"]
    dashboard, all_linked_entities = update_db_get_linked_entities(dashboard, to_acct, to_name)
    logger.debug(json.dumps(all_linked_entities))
    db_file_name = str(to_acct) + "-" + dashboard['name'] + ".json"
    store.save_json_to_file(dashboard, db_file_name)
    result = db_entity.create(to_api_key, to_acct, dashboard)
    if "errors" in result["response"]["data"]["dashboardCreate"]["entityResult"]:
        logger.error(json.dumps(result))
    else:
        logger.info("Dashboard copied to " + str(to_acct) + " as " +
                    result["response"]["data"]["dashboardCreate"]["entityResult"]["name"])
        tgt_db_guid = result["response"]["data"]["dashboardCreate"]["entityResult"]["guid"]
        logger.info("Now updating linked entities")
        update_linked_entities(to_api_key, all_linked_entities, tgt_db_guid)
        logger.info(ec.get_permalink(to_api_key, tgt_db_guid))


def map_page_to_guid(dashboard):
    page_guids = {}
    for page in dashboard['pages']:
        page_guids[page['name']] = page['guid']
    return page_guids


def update_linked_entities(to_api_key, all_linked_entities, dashboard_guid):
    result = db_entity.get_pages_widgets(to_api_key, dashboard_guid)
    dashboard = result['response']['data']['actor']['entity']
    logger.info(json.dumps(dashboard))
    page_guids = map_page_to_guid(dashboard)
    logger.info(json.dumps(page_guids))
    for page in dashboard['pages']:
        page_widgets = []
        for widget in page['widgets']:
            wid_key = widget_key(page['name'], widget['title'])
            if wid_key in all_linked_entities:
                linked_entities = all_linked_entities[wid_key]
                linkedEntityGuids = [page_guids[linked_entities[0]['name']]]
                widget['linkedEntityGuids'] = linkedEntityGuids
                page_widgets.append(widget)
        if not page_widgets:
            logger.info("No linked entities in " + page['name'])
        else:
            logger.info("Updating linked entities for " + page['name'])
            result = db_entity.update_page_widgets(to_api_key, page['guid'], page_widgets)
            if result['response']['data']['dashboardUpdateWidgetsInPage']['errors'] is None:
                logger.info("Successfully updated facets for " + page['name'])
            else:
                logger.error(json.dumps(result))


def update_db_get_linked_entities(dashboard, to_acct, to_name):
    all_linked_entities = {}
    src_db_name_prefix = dashboard['name'] + ' / '
    dashboard['name'] = to_name
    all_linked_entities['pages'] = []
    for page in dashboard['pages']:
        for widget in page['widgets']:
            if 'nrqlQueries' in widget['rawConfiguration']:
                for nrqlQuery in widget['rawConfiguration']['nrqlQueries']:
                    nrqlQuery['accountId'] = to_acct
            linkedEntities = widget.pop('linkedEntities', None)
            if linkedEntities is not None:
                for linkedEntity in linkedEntities:
                    db_page_name = linkedEntity['name']
                    if db_page_name.startswith(src_db_name_prefix):
                        linkedEntity['name'] = db_page_name[db_page_name.rindex('/') + 2:]
                all_linked_entities[widget_key(page["name"], widget["title"])] = linkedEntities
    return dashboard, all_linked_entities


def widget_key(page_name, widget_title):
    return page_name + "-" + widget_title


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy/Download Dashboard')
    setup_params(parser)
    args = parser.parse_args()
    if args.download:
        download(args.fromApiKey[0], args.entityGuid[0])
    elif args.copy or args.updateFacets:
        if not args.toApiKey:
            logger.info("No toApiKey provided. Assuming fromApiKey will work for the toAccount")
            to_api_key = args.fromApiKey[0]
        else:
            to_api_key = args.toApiKey[0]
        if not args.toName:
            to_name = NO_NAME
        else:
            to_name = args.toName[0]
        copy_dashboard(args.fromApiKey[0], args.entityGuid[0], args.toAccount[0], to_api_key, to_name)
