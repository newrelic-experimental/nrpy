import os
import requests
import json
import library.nrpylogger as nrpy_logger
from library.endpoints import Endpoints

URL = 'https://api.newrelic.com/graphql'

logger = nrpy_logger.get_logger(os.path.basename(__file__))


class GraphQl:

    def __init__(self):
        pass

    @staticmethod
    def post(per_api_key, payload, region=Endpoints.REGION_US):
        result = {}
        response = requests.post(Endpoints.of(region).GRAPHQL_URL, headers=GraphQl.headers(per_api_key),
                                 data=json.dumps(payload))
        result['status'] = response.status_code
        if response.text:
            response_json = response.json()
            if 'errors' in response_json:
                logger.error('Error : ' + response.text)
                result['error'] = response_json['errors']
            else:
                logger.debug('Success : ' + response.text)
                result['response'] = response_json
        return result

    @staticmethod
    def headers(api_key):
        return {'api-key': api_key, 'Content-Type': 'application/json'}