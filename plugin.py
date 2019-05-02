import json
import os
import sys

import requests


if __name__ == '__main__':
    try:
        url = os.environ['PLUGIN_URL'] + '/api'
        username = os.environ['PLUGIN_USERNAME']
        password = os.environ['PLUGIN_PASSWORD']
        stack = os.environ['PLUGIN_STACK']
    except KeyError:
        print('Missing required settings.')
        sys.exit(1)

    endpoint = os.getenv('PLUGIN_ENDPOINT') or 'primary'

    stackfile = os.getenv('PLUGIN_STACKFILE') or 'docker-stack.yml'
    environment = json.loads(os.getenv('PLUGIN_ENVIRONMENT') or '[]')

    env = []
    for e in environment:
        env.append({
            'name': e,
            'value': environment[e]
        })

    r = requests.post(
        url + '/auth', json={
            'Username': username,
            'Password': password
        }
    )

    print(r.text)

    headers = {
        'Authorization': 'Bearer ' + r.json()['jwt']
    }

    if os.path.isfile(stackfile):
        with open(stackfile) as f:
            stackfilecontent = f.read()
    else:
        print('No stackfile found.')
        sys.exit(1)

    id = None
    for s in requests.get(url + '/stacks', headers=headers).json():
        if s['Name'] == stack:
            id = str(s['Id'])
            endpointId = str(s['EndpointId'])

    if id is None:
        print('Creating stack "{}"'.format(stack))

        for e in requests.get(url + '/endpoints', headers=headers).json():
            if e['Name'] == endpoint:
                endpointId = str(e['Id'])

        swarmId = str(requests.get(
            url + '/endpoints/' + endpointId + '/docker/info',
            headers=headers
        ).json()['Swarm']['Cluster']['ID'])

        r = requests.post(
            url + '/stacks?' +
            'type=1&method=string&endpointId=' + endpointId,
            headers=headers,
            json={
                'Name': stack,
                'SwarmID': swarmId,
                'StackFileContent': stackfilecontent,
                'Env': env,
                'Prune': False
            }
        )
    else:
        print('Updating stack "{}"'.format(stack))

        r = requests.put(
            url + '/stacks/' + id + '?endpointId=' + endpointId,
            headers=headers,
            json={
                'StackFileContent': stackfilecontent,
                'Env': env,
                'Prune': True
            }
        )
