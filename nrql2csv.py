import json
import os
import library.localstore as store
import library.clients.nrqlclient as nrqlclient
from library.endpoints import Endpoints
import library.nrpylogger as nrpylogger


logger = nrpylogger.get_logger(os.path.basename(__file__))
config = store.load_json_from_file(".","nrql2csv.json")
nrqls = config["nrql"]
since_hours_ago = config["since_days_ago"] * 24
query_increment_hours = config["query_increment_hours"]
timeout = config["timeout"]
batch_count = int(since_hours_ago/query_increment_hours)
region = Endpoints.REGION_US
if 'region' in config:
    region = config['region']
for nrql in nrqls:
    logger.info('Running query {nrql["name"]}')
    merged_results = {}
    for batch in range(batch_count):
        since_hours = since_hours_ago - batch * query_increment_hours
        until_hours = since_hours_ago - (batch + 1) * query_increment_hours
        query = f'FROM {nrql["from"]} SELECT {nrql["select"]} AS `output` WHERE {nrql["where"]} FACET {nrql["facet"]}' \
                f' SINCE {str(since_hours)} HOURS AGO UNTIL {str(until_hours)} HOURS AGO LIMIT MAX'
        logger.info(query)
        response = nrqlclient.get_results(query, config['account_id'], config['nr_user_api_key'], timeout, region)
        if 'error' in response:
            logger.error(json.dumps(response))
            logger.error('correct the config to proceed')
            break
        if 'results' in response:
            batch_result = {result['facet']: result['output'] for result in response['results']}
            for key, value in batch_result.items():
                merged_results[key] = merged_results.get(key, 0) + value
        else:
            logger.info('no results for this query trying next batch')
    header = {nrql["facet"]: "summedOutput"}
    store.save_dict_as_csv(f'{nrql["name"]}.csv', merged_results, header)






