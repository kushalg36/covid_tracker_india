import requests
from auth import SLACK_WEBHOOK
import logging
import json

headers = {
    'Content-type': 'application/json',
}

def slack(url=SLACK_WEBHOOK):
    def send(msg):
        logging.info('Sending {msg} to slack'.format(msg=msg))
        payload = {'text':msg}
        return requests.post(SLACK_WEBHOOK, headers=headers, data=json.dumps(payload))
    return send