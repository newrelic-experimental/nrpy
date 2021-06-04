import os
import argparse
import json
from library import utils
import library.clients.entityclient as entityclient
import library.nrpylogger as nrpylogger


ec = entityclient.EntityClient()
logger = nrpylogger.get_logger(os.path.basename(__file__))
    

def setup_params(parser):
    parser.add_argument('--personalApiKey', nargs=1, type=str, required=True, help='Personal API Key')
    parser.add_argument('--delTagValues', nargs=1, type=str, required=False, help='delete tag values e.g.owner=John')
    parser.add_argument('--addTags', nargs=1, required=False, help='new tag e.g. owner=Jack')
    parser.add_argument('--rmAllInfraHostTags', dest='rmAllInfraHostTags', required=False, action='store_true',
                        help='Remove all tags from infra hosts')
    parser.add_argument('--getAllInfraHostTags', dest='getAllInfraHostTags', required=False, action='store_true',
                        help='Get all mutable tags from infra hosts')


def print_params():
    logger.info("personalApiKey : " + len(personal_api_key[:-4])*"*"+personal_api_key[-4:])
    if args.delTagValues:
        logger.info("delTagValues : " + str(args.delTagValues[0]))
    if args.addTags:
        logger.info("addTags : " + str(args.addTags[0]))
    if args.rmAllInfraHostTags:
        logger.info("Remove all editable tags from infra hosts")
    if args.getAllInfraHostTags:
        logger.info("Get all editable tags from all infra hosts")


def update_tags(per_api_key, del_tag_values, add_tags):
    del_tag_values_arr = del_tag_values.split(",")
    addTagsArr = add_tags.split(",")
    result = ec.gql_get_entities_with_tags(per_api_key, del_tag_values_arr)
    if 'error' in result:
        logger.error(json.dumps(result['error']), utils.DEFAULT_INDENT)
        logger.error("Error in executing NerdGraph query.")
        return
    if result['count'] > 0:
        for entity in result['entities']:
            logger.info('Processing ' + entity['entityType'] + ':' + entity['name'])
            rm_result = ec.gql_mutate_delete_tag_values(per_api_key, entity['guid'], del_tag_values_arr)
            if not rm_result['response']['data']['taggingDeleteTagValuesFromEntity']['errors']:
                logger.info('Tag ' + del_tag_values + ' Removed to ' + entity['entityType'] + ':' + entity['name'])
            add_result = ec.gql_mutate_add_tags(per_api_key, entity['guid'], addTagsArr)
            if not add_result['response']['data']['taggingAddTagsToEntity']['errors']:
                logger.info('Tag ' + add_tags + ' Added to ' + entity['entityType'] + ':' + entity['name'])
    else:
        logger.warning("No entities found matching " + del_tag_values)


def remove_all_infra_tags(per_api_key):
    infraTags = {'mutableTags': []}
    result = ec.gql_get_entities_of_type(per_api_key, "INFRA", "HOST")
    if 'error' in result:
        logger.error(json.dumps(result['error']), utils.DEFAULT_INDENT)
        logger.error("Error in executing NerdGraph query.")
        infraTags['error'] = json.dumps(result['error'])
        return infraTags
    if result['count'] > 0:
        for entity in result['entities']:
            logger.info('Processing ' + entity['type'] + ':' + entity['name'])
            result = ec.gql_get_tags_with_metadata(per_api_key, entity['guid'])
            mutableTags = []
            for tag in result['response']['data']['actor']['entity']['tagsWithMetadata']:
                if tag['values'][0]['mutable']:
                    mutableTags.append(tag['key'])
            if mutableTags:
                logger.info('deleting tags for ' + entity['name'] + " : " + json.dumps(mutableTags))
                result = ec.gql_mutate_delete_tag_keys(per_api_key, entity['guid'], mutableTags)
                if not result['response']['data']['taggingDeleteTagFromEntity']['errors']:
                    logger.info('Deleted tags for ' + entity['name'] + " : " + json.dumps(mutableTags))
                else:
                    logger.error("Error deleting tags for " + entity['name'] + json.dumps(result))
            else:
                logger.info('No mutable tags found for ' + entity['name'])
    else:
        logger.warning("No entities found matching domain INFRA type HOST")


def get_all_infra_tags(per_api_key):
    infraTags = {'mutableTags': []}
    result = ec.gql_get_entities_of_type(per_api_key, "INFRA", "HOST")
    if 'error' in result:
        logger.error(json.dumps(result['error']), utils.DEFAULT_INDENT)
        logger.error("Error in executing NerdGraph query.")
        infraTags['error'] = json.dumps(result['error'])
        return infraTags
    if result['count'] > 0:
        for entity in result['entities']:
            logger.info('Processing ' + entity['type'] + ':' + entity['name'])
            result = ec.gql_get_tags_with_metadata(per_api_key, entity['guid'])
            mutableTags = []
            for tag in result['response']['data']['actor']['entity']['tagsWithMetadata']:
                if tag['values'][0]['mutable']:
                    mutableTags.append(tag['key'])
            logger.info(entity['name'] + ' mutable tags ' + json.dumps(mutableTags))
    else:
        logger.warning("No entities found matching domain INFRA type HOST")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update tags for all entities from one value to another')
    setup_params(parser)
    args = parser.parse_args()
    personal_api_key = utils.ensure_personal_api_key(args)
    if not personal_api_key:
        utils.error_and_exit('personalApiKey', 'ENV_PERSONAL_API_KEY')
    print_params()
    if args.getAllInfraHostTags:
        get_all_infra_tags(personal_api_key)
    elif args.rmAllInfraHostTags:
        remove_all_infra_tags(personal_api_key)
    else:
        update_tags(personal_api_key, args.delTagValues[0], args.addTags[0])
