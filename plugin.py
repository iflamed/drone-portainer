import json
import os
import sys

import requests

const_tag = '${DOCKER_TAG}'
const_repo = '${DOCKER_REPO}'

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

    tag = os.getenv('DRONE_TAG') or 'latest'
    if tag.startswith('v'):
        tag = tag[len('v'):]

    repo = os.getenv('PLUGIN_REPO') or ''
    debug = os.getenv('PLUGIN_DEBUG') or ''

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
    if debug != '':
        print(r.text)

    headers = {
        'Authorization': 'Bearer ' + r.json()['jwt']
    }

    if os.path.isfile(stackfile):
        with open(stackfile, encoding='utf-8') as f:
            stackfilecontent = f.read()
    else:
        print('No stackfile found.')
        sys.exit(1)

    # replace deploy tag
    stackfilecontent = stackfilecontent.replace(const_tag, tag)
    stackfilecontent = stackfilecontent.replace(const_repo, repo)
    if debug != '':
        print(stackfilecontent)

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

    if r.status_code == 200:
        print('Done.')
    else:
        print(r.text)