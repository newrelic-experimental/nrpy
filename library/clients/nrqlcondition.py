import json
import os
import library.nrpylogger as nrpy_logger
import library.clients.gql as nerdgraph

logger = nrpy_logger.get_logger(os.path.basename(__file__))


class NrqlCondition:

    def __init__(self):
        pass

    @staticmethod
    def search(user_api_key, account_id, event_metric_name):
        payload = NrqlCondition._search_conditions_payload(account_id, event_metric_name)
        logger.debug(json.dumps(payload))
        result = nerdgraph.GraphQl.post(user_api_key, payload, "")
        while result['nextCursor']:
            payload = NrqlCondition._search_conditions_payload(account_id, event_metric_name,  result['nextCursor'])
            nextResult = nerdgraph.GraphQl.post(user_api_key, payload)







    @staticmethod
    def _search_conditions_payload(account_id, event_metric_name, next_cursor=""):
        search_conditions_query = '''query($accountId: Int!, $eventMetricName: String!, $cursor: String!) { 
                                actor {
                                    account(id: $accountId) {
                                        alerts {
                                            nrqlConditionsSearch(searchCriteria: {queryLike: $eventMetricName}, 
                                            cursor: $next_cursor) {
                                                nrqlConditions { name enabled }
                                                totalCount
                                                nextCursor
                                            }
                                        }                           
                                    }
                                } 
                            }'''
        variables = {'accountId': account_id, 'eventMetricName': event_metric_name, 'cursor': next_cursor}
        return {'query': search_conditions_query, 'variables': variables}