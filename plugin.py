import json
import os

import requests


if __name__ == '__main__':
    url = os.environ['PLUGIN_URL'] + '/api'
    username = os.environ['PLUGIN_USERNAME']
    password = os.environ['PLUGIN_PASSWORD']
    stack = os.environ['PLUGIN_STACK']

    print('updating stack: ' + stack)

    credentials = {
        'Username': username,
        'Password': password
    }

    print(json.dumps(credentials))

    jwt = requests.post(url + '/auth', json=credentials).json()['jwt']

    headers = {
        'Authorization': 'Bearer ' + jwt
    }

    for e in requests.get(url + '/endpoints', headers=headers).json():
        if e['Name'] == 'primary':
            endpointId = str(e['Id'])

    for s in requests.get(url + '/stacks', headers=headers).json():
        if s['Name'] == stack:
            id = str(s['Id'])

    env = requests.get(
        url + '/stacks/' + id,
        headers=headers).json()['Env']
    stackfilecontent = requests.get(
        url + '/stacks/' + id + '/file',
        headers=headers).json()['StackFileContent']

    r = requests.put(
        url + '/stacks/' + id + '?endpointId=' + endpointId,
        headers=headers,
        json={
            'StackFileContent': stackfilecontent,
            'Env': env,
            'Prune': False
        }
    )
