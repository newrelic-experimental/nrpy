import os
import argparse
import json
import library.clients.apiaccessclient as apiaccessclient
import library.localstore as store
import library.nrpylogger as nrpylogger


aac = apiaccessclient.ApiAccess()
logger = nrpylogger.get_logger(os.path.basename(__file__))


def setup_params(parser):
    parser.add_argument('--userApiKey', nargs=1, type=str, required=True, help='User API Key')
    parser.add_argument('--createUserKey', dest='createUserKey', required=False, action='store_true',
                        help='Create User Key')
    parser.add_argument('--queryUserKey', dest='queryUserKey', required=False, action='store_true',
                        help='Query User Key')
    parser.add_argument('--accountId', nargs=1, type=int, required=True, help='accountId')
    parser.add_argument('--apiKeyName', nargs=1, type=str, required=True, help='API Key Name. '
                                                                               'Required for create and query')
    parser.add_argument('--notes', nargs=1, type=str, required=False, help='API Key Notes. Optional for create')
    parser.add_argument('--userId', nargs=1, type=int, required=False, help='int userID for which user key is '
                                                                            'generated. Required for create')


def print_params():
    logger.info("accountId : " + str(args.accountId[0]))
    logger.info("userApiKey : " + len(args.userApiKey[:-4]) * "*" + args.userApiKey[-4:])
    logger.info("name : " + args.apiKeyName[0])
    if args.createUserKey:
        if args.notes:
            logger.info("notes : " + args.notes[0])
        else:
            logger.info("make up the notes")


def query_user_api_key(user_api_key, acct_id, user_id, api_key_name):
    result = aac.get_user_api_key(user_api_key, acct_id, user_id)
    logger.info(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='query/create User API Key')
    setup_params(parser)
    args = parser.parse_args()
    if args.queryUserKey:
        query_user_api_key(args.userApiKey[0], args.accountId[0], args.userId[0], args.apiKeyName[0])
    elif args.createUserApiKey:
        if not args.toApiKey:
            logger.info("No toApiKey provided. Assuming fromApiKey will work for the toAccount")
            to_api_key = args.fromApiKey[0]
        else:
            to_api_key = args.toApiKey[0]

