import os
import argparse
import json
from library import utils
import library.clients.nrqlcondition as nrqlcondition
import library.clients.entityclient as entityclient
import library.localstore as store
import library.nrpylogger as nrpylogger


nrqlcondition = nrqlcondition.NrqlCondition()
logger = nrpylogger.get_logger(os.path.basename(__file__))


def setup_params(parser):
    parser.add_argument('--accountId', nargs=1, type=int, required=True, help='accountId')
    parser.add_argument('--userApiKey', nargs=1, type=str, required=True, help='User API Key')
    parser.add_argument('--searchStringsFile', nargs=1, type=str, required=True, help='')

def print_params(user_api_key):
    logger.info("accountId : " + str(args.accountId[0]))
    logger.info("userApiKey : " + len(user_api_key[:-4]) * "*" + user_api_key[-4:])
    logger.info("searchStringsFile : " + args.searchStringsFile[0])


def search_nrql_conditions(user_api_key, account_id, search_strings_file):
    event_metric_names = store.load_names(search_strings_file)
    nrql_conditions = [['eventMetricName', 'totalCount', 'conditionName', 'enabled']]
    for event_metric_name in event_metric_names:
        result = nrqlcondition.search(user_api_key,account_id,event_metric_name)
        logger.info(json.dumps(result))
        total = result['response']['data']['actor']['account']['alerts']['nrqlConditionsSearch']['totalCount']
        conditions = result['response']['data']['actor']['account']['alerts']['nrqlConditionsSearch']['nrqlConditions']
        if result['status'] == 200 and total > 0:
            for condition in conditions:
                nrql_conditions.append([event_metric_name,total,condition['name'],condition['enabled']])
        else:
            nrql_conditions.append([event_metric_name, total, '', ''])
    store.save_csv('nrqlConditions.csv',nrql_conditions)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search NRQL Conditions')
    setup_params(parser)
    args = parser.parse_args()
    api_key = utils.ensure_user_api_key(args)
    if not api_key:
        utils.error_and_exit('userApiKey', 'ENV_USER_API_KEY')
    print_params(api_key)
    search_nrql_conditions(api_key, args.accountId[0], args.searchStringsFile[0])
