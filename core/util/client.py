# coding: utf-8

import json
import requests
from fabkit import api


@api.task
def client():
    print 'DEBUG'
    payload = {
        'username': 'admin',
        'password': 'admin',
    }
    headers = {
        'Accept': 'application/json',
    }

    result = requests.post('http://127.0.0.1:8080/api/authtoken/',
                           data=payload,
                           headers=headers)

    if result.status_code == 200:
        token = json.loads(result.text)['token']
        headers = {
            'Authorization': 'Token {0}'.format(token),
        }
        payload = {
            'name': 'test'
        }
        print token
        # curl -v -X POST http://127.0.0.1:8080/api/files/ -F datafle=@httpd.conf -H 'Authorization: Token a52ca843731f47ff3a55fd86111299ef52b2a417'  # noqa
        result = requests.post('http://127.0.0.1:8080/api/groups/',
                               data=payload,
                               headers=headers)
        print result.status_code
        print result.text
    else:
        print result.status_code
        print result.text
