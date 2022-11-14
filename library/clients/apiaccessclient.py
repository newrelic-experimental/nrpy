import json
import os
import library.nrpylogger as nrpy_logger
import library.clients.gql as nerdgraph

logger = nrpy_logger.get_logger(os.path.basename(__file__))


class ApiAccess:

    def __init__(self):
        pass

    @staticmethod
    def get_user_api_key(user_api_key, account_id, user_id):
        payload = ApiAccess._query_user_key_payload(account_id, user_id)
        logger.debug(json.dumps(payload))
        return nerdgraph.GraphQl.post(user_api_key, payload)

    @staticmethod
    def create_user_api_key(user_api_key, account_id, user_id, api_key_name, notes):
        payload = ApiAccess._create_user_key_payload(account_id, api_key_name, notes, user_id)
        logger.debug(json.dumps(payload))
        return nerdgraph.GraphQl.post(user_api_key, payload)

    @staticmethod
    def _create_user_key_payload(account_id, name, notes, user_id):
        mutation_query = '''mutation($accountId: Int!, $name: String, $notes: String, $userId: Int!) {                    
                    apiAccessCreateKeys(accountId: $accountId , name: $name, notes: $notes, userId: $userId) {
                        createdKeys { 
                            ... on ApiAccessUserKey { id name key accountId userId } 
                        }
                        errors { message type }
                    }
                }'''
        return {'query': mutation_query,
                'variables': {'accountId': account_id, 'name': name, 'notes': notes, 'userId': user_id}}

    @staticmethod
    def _query_user_key_payload(account_id, user_id):
        query = '''query($accountIds: [Int], $userIds: [Int]) { 
                                actor { 
                                    apiAccess {
                                        keySearch(query: {scope: {accountIds: $accountIds, userIds: $userIds}, 
                                            types: USER}) {
                                                keys {
                                                        id
                                                        key
                                                        name
                                                        notes
                                                }
                                        } 
                                    }
                                }
                            }'''
        variables = {'accountIds': [account_id],'userIds': [user_id] }
        return {'query': query, 'variables': variables}

