import os
import argparse
import json
import csv
from datetime import date
from library import utils
import library.clients.dbentityclient as dbclient
import library.clients.alertsaiclient as alertsaiclient
import library.localstore as store
import library.nrpylogger as nrpylogger

alertsaiclient = alertsaiclient.AlertsAI()
logger = nrpylogger.get_logger(os.path.basename(__file__))

config = store.load_json_from_file(".", "alertsai.json")
nr_user_api_key = config['nr_user_api_key']
accountId = config['accountId']


def get_all_policies(nr_user_api_key, accountId, nextCursor=None):
    all_policies = []
    while True:
        result = alertsaiclient.get_all_policies_nrql(nr_user_api_key, accountId, nextCursor)
        policies = result['response']['data']['actor']['account']['alerts']['policiesSearch']
        nextCursor = policies['nextCursor']
        for policy in policies['policies']:
            all_policies.append({
                "policyId": policy['id'],
                "policyName": policy['name']
            })
        # Break the loop if there is no next cursor
        if not nextCursor:
            break

        logger.info("List of all policies have been generated.")
    return all_policies


def get_all_policy_conditions(nr_user_api_key, accountId, policyId, policyName, nextCursor):
    conditions_list = []
    invalid_policy_list = []
    empty_policy_list = []
    while True:
        result = alertsaiclient.get_policy_conditions_nrql(nr_user_api_key, accountId, policyId, policyName, nextCursor)
        if 'error' in result:
            logger.error(json.dumps(result))
            logger.info(str(policyId) + " is an invalid policy.")
            invalid_policy_list.append({'policyId': policyId, 'policyName': policyName})
            return conditions_list, empty_policy_list, invalid_policy_list
        else:
            conditions = result['response']['data']['actor']['account']['alerts']['nrqlConditionsSearch']
            nextCursor = conditions['nextCursor']
            # If there are no conditions, add the policy to the empty policy list
            if not conditions['nrqlConditions']:
                logger.info(str(policyId) + " has no conditions.")
                empty_policy_list.append({'policyId': policyId, 'policyName': policyName})
                return conditions_list, empty_policy_list, invalid_policy_list
            else:
                result_condition_list = conditions['nrqlConditions']
        for condition in result_condition_list:
            conditions_list.append({
                "policyId": policyId,
                "policyName": policyName,
                "conditionId": condition['id'],
                "conditionName": condition['name'],
                "conditionQuery": condition['nrql']['query'],
                "enabled": condition['enabled']
            })

        # Break the loop if there is no next cursor
        if not nextCursor:
            logger.info("List of all conditions have been generated.")
            break
    return conditions_list, invalid_policy_list, empty_policy_list


def generate_policies_and_conditions_report():
    policies_and_conditions_report_filename =  "policies_and_conditions_report-"+str(date.today())+".csv"
    invalid_policies_report_filename = "invalid_policies_report-"+str(date.today())+".csv"
    empty_policies_report_filename = "empty_policies_report-"+str(date.today())+".csv"
    policies_and_conditions_report = []
    invalid_policies_report = []
    empty_policies_report = []
    all_policies_list = get_all_policies(nr_user_api_key, accountId, nextCursor=None)
    for policy in all_policies_list:
        conditions_list, invalid_policies_list, empty_policies_list = get_all_policy_conditions(nr_user_api_key, accountId, policy['policyId'], policy['policyName'], nextCursor=None)
        if conditions_list:
            for condition in conditions_list:
                policies_and_conditions_report.append(condition)
        if invalid_policies_list:
            for temp_policy in invalid_policies_list:
                invalid_policies_report.append(temp_policy)

        if empty_policies_list:
            for temp_policy in empty_policies_list:
                empty_policies_report.append(temp_policy)
    # Creating CSV Reports
    store.save_list_of_dict_as_csv(policies_and_conditions_report, policies_and_conditions_report_filename)
    logger.info("Policies and Conditions Report has been saved as " + policies_and_conditions_report_filename)
    store.save_list_of_dict_as_csv(invalid_policies_report, invalid_policies_report_filename)
    logger.info("Invalid Policies Report has been saved as " + invalid_policies_report_filename)
    store.save_list_of_dict_as_csv(empty_policies_report, empty_policies_report_filename)
    logger.info("Empty Policies Report has been saved as " + empty_policies_report_filename)


if __name__ == '__main__':
    generate_policies_and_conditions_report()
