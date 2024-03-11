import requests
import json
import os
import library.utils as utils
import library.localstore as store
import library.nrpylogger as nrpy_logger
import library.clients.gql as nerdgraph

logger = nrpy_logger.get_logger(os.path.basename(__file__))


class AlertsAI:

    def __init__(self):
        pass

    @staticmethod
    def get_all_policies_nrql(nr_user_api_key, accountId, nextCursor):
        payload = AlertsAI.get_all_policies_payload(accountId, nextCursor)
        logger.debug(json.dumps(payload))
        return nerdgraph.GraphQl.post(nr_user_api_key, payload)

    @staticmethod
    def get_policy_conditions_nrql(nr_user_api_key, accountId, policyId, policyName, nextCursor):
        payload = AlertsAI.get_policy_conditions_payload(accountId, policyId, policyName, nextCursor)
        logger.debug(json.dumps(payload))
        return nerdgraph.GraphQl.post(nr_user_api_key, payload)

    def get_all_policies_payload(accountId, nextCursor=None):
        if nextCursor:
            policy_query = '''query ($accountId:Int!) {
                  actor {
                    account(id: $accountId) {
                      alerts {
                        policiesSearch(cursor: "%s") {
                          policies {
                            id
                            name
                          }
                          nextCursor
                          totalCount
                        }
                      }
                    }
                  }
                }
                ''' % (nextCursor)
            variables = {'accountId': accountId}
        else:
            policy_query = '''query($accountId: Int!) {
                                actor {
                                    account(id: $accountId) {
                                      alerts {
                                        policiesSearch {
                                          policies {
                                            id
                                            name
                                          }
                                          nextCursor
                                          totalCount
                                        }
                                      }
                                    }
                                  }
                                }'''
            variables = {'accountId': accountId}
        return {'query': policy_query, 'variables': variables}

    def get_policy_conditions_payload(accountId, policyId, policyName, nextCursor=None):
        if nextCursor:
            conditions_query = """query ($accountId: Int!, $policyId: ID) {
                              actor {
                                account(id: $accountId) {
                                  alerts {
                                    nrqlConditionsSearch(searchCriteria: {policyId: $policyId}, cursor: "%s") {
                                      nextCursor
                                      nrqlConditions {
                                        enabled
                                        name
                                        id
                                        nrql {
                                          query
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }""" % (nextCursor)
            variables = {'accountId': accountId, 'policyId': policyId}
        else:
            conditions_query = """query ($accountId: Int!, $policyId: ID) {
                              actor {
                                account(id: $accountId) {
                                  alerts {
                                    nrqlConditionsSearch(searchCriteria: {policyId: $policyId}) {
                                      nextCursor
                                      nrqlConditions {
                                        enabled
                                        name
                                        id
                                        nrql {
                                          query
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }"""
            variables = {'accountId': accountId, 'policyId': policyId}
        return {'query': conditions_query, 'variables': variables}