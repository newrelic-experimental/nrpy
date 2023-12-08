import library.clients.gql as nerdgraph


def get_results(query, account_id, api_key, timeout, region):
    query_response = {}
    error = {}
    payload = payload_from(query, account_id, timeout)
    nerdgraph_response = nerdgraph.GraphQl.post(api_key,payload,region)
    if 'response' in nerdgraph_response:
        response = nerdgraph_response['response']
        query_response['results'] = response['data']['actor']['nrql']['results']
        return query_response
    if 'error' in nerdgraph_response:
        error['errorClass'] = nerdgraph_response['error'][0]['extensions']['errorClass']
        error['locations'] = nerdgraph_response['error'][0]['locations'][0]
        error['message'] = nerdgraph_response['error'][0]['message']
        query_response['error'] = error
        return query_response


def payload_from(query, account_id, timeout):
    exec_nrql = '''query execNrql($accountId: Int!, $nrqlQuery: Nrql!, $timeout: Seconds!) {
                          actor {
                            nrql(
                              accounts: [$accountId]
                              query: $nrqlQuery
                              timeout: $timeout
                            ) {
                              results
                            }
                          }
                        }
                        '''
    variables = {'accountId': account_id, 'nrqlQuery': query, 'timeout': timeout}
    payload = {'query': exec_nrql, 'variables': variables}
    return payload