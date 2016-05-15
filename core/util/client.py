# coding: utf-8

import shutil
import json
import requests
import commands
import os
from oslo_config import cfg
from fabkit import api

CONF = cfg.CONF

endpoint = '{0}/api/'.format(CONF.client.endpoint)


def download(headers, group, filename, path):
    result = requests.get(
        '{0}files/{1}/?name={2}'.format(
            endpoint, group, filename),
        headers=headers, stream=True)

    print result.status_code
    if result.status_code == 200:
        print result.status_code
        with open(path, 'wb') as f:
            result.raw.decode_content = True
            shutil.copyfileobj(result.raw, f)


@api.task
def client(*args, **kwargs):
    payload = {
        'username': CONF.client.username,
        'password': CONF.client.password,
    }

    headers = {
        'Accept': 'application/json',
    }

    result = requests.post('{0}authtoken/'.format(endpoint),
                           data=payload,
                           headers=headers)

    if result.status_code != 200:
        print result.status_code
        print result.text
        return

    token = json.loads(result.text)['token']
    headers = {
        'Authorization': 'Token {0}'.format(token),
    }
    print token
    print args

    if args[0] == 'help':
        print 'help'

    elif args[0] == 'create_group':
        if len(args) != 2:
            print 'create_group [group_name]'
            return

        payload = {
            'name': args[1],
        }
        result = requests.post('{0}groups/'.format(endpoint),
                               data=payload,
                               headers=headers)

        print result.status_code
        print result.text

    elif args[0] == 'user_group':
        if len(args) != 3:
            print 'user_group [user] [group_name]'
            return

        payload = {
            'group': args[2],
        }

        result = requests.put('{0}users/{1}/'.format(endpoint, args[1]),
                              data=payload,
                              headers=headers)

        print result.status_code
        print result.text

    elif args[0] == 'upload':
        if len(args) == 2 and args[1] == 'fabkit':
            status, output = commands.getstatusoutput(
                'rm -rf /tmp/fabkit-repo && '
                'cp -r {0} /tmp/fabkit-repo && '
                'rm -rf /tmp/fabkit-repo/fabfile/core/webapp && '
                'rm -rf /tmp/fabkit-repo/storage/tmp && '
                'find /tmp/fabkit-repo -name .git | xargs rm -rf && '
                'find /tmp/fabkit-repo -name .tox | xargs rm -rf && '
                'find /tmp/fabkit-repo -name test-repo | xargs rm -rf && '
                'find /tmp/fabkit-repo -name *.pyc | xargs rm -rf && '
                'cd /tmp/ && tar cfz fabkit-repo.tar.gz fabkit-repo'.format(CONF._repo_dir))

            files = {'datafile': open('/tmp/fabkit-repo.tar.gz', 'rb')}

            payload = {
                'name': 'fabkit',
                'group': CONF.client.group,
            }

        elif len(args) != 4:
            print 'upload [group_name] {file_name} {file_path}'
            return

        else:
            files = {'datafile': open(args[3], 'rb')}

            payload = {
                'name': args[2],
                'group': args[1],
            }

        result = requests.post('{0}files/'.format(endpoint),
                               data=payload,
                               files=files,
                               headers=headers)

        print result.status_code
        print result.text

    elif args[0] == 'download':
        if len(args) != 4:
            print 'download [group_name] {file_name} {file_path}'
            return

        download(headers, args[1], args[2], args[3])

    elif args[0] == 'setup':
        if len(args) != 1:
            print 'setup'
            return

        download(headers, CONF.client.group, 'fabkit', '/opt/fabkit/var/fabkit-repo.tar.gz')

        status, output = commands.getstatusoutput(
            'cd /opt/fabkit/var && rm -rf fabkit-repo && tar xf fabkit-repo.tar.gz')

        status, output = commands.getstatusoutput(
            'cp {0} /opt/fabkit/var/fabkit-repo'.format(CONF._inifile))

        for cluster in CONF.client.clusters:
            print cluster
            node = os.path.join(cluster, CONF.host)
            for task in CONF.client.task_patterns:
                status, output = commands.getstatusoutput(
                    '/opt/fabkit/bin/fab -f /opt/fabkit/var/fabkit-repo/fabfile '
                    'node:{0},local manage:{1}'.format(node, task))
                print output
