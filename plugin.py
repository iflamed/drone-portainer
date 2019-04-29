import os

import requests


if __name__ == '__main__':
    url = (os.getenv('PLUGIN_URL') or '') + '/api'
    username = os.environ['PLUGIN_USERNAME']
    password = os.environ['PLUGIN_PASSWORD']
    stack = os.getenv('PLUGIN_STACK') or ''
    endpoint = os.getenv('PLUGIN_ENDPOINT') or 'primary'

    print('updating stack: ' + stack)

    jwt = requests.post(
        url + '/auth',
        json={
            'Username': username,
            'Password': password
        }
    ).json()['jwt']

    headers = {
        'Authorization': 'Bearer ' + jwt
    }

    for e in requests.get(url + '/endpoints', headers=headers).json():
        if e['Name'] == endpoint:
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
