# coding: utf-8

import pickle
import shutil
import json
import requests
import commands
import os
import sys
import subprocess
from oslo_config import cfg
from oslo_log import log as logging
from fabkit import api

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

endpoint = '{0}/api/'.format(CONF.client.endpoint)


def download(headers, group, filename, path):
    result = requests.get(
        '{0}files/{1}/?name={2}'.format(
            endpoint, group, filename),
        headers=headers, stream=True)

    if result.status_code == 200:
        with open(path, 'wb') as f:
            result.raw.decode_content = True
            shutil.copyfileobj(result.raw, f)


def get_auth_headers():
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
    return headers


@api.task
def client(*args, **kwargs):

    if args[0] == 'help':
        print 'help'

    elif args[0] == 'create_superuser':
        if sys.exec_prefix == '/usr':
            prefix = ''
        else:
            prefix = '{0}/bin/'.format(sys.exec_prefix)
        subprocess.call('cd {0} && {1}python manage.py createsuperuser'.format(
            CONF._webapp_dir, prefix), shell=True)

    elif args[0] == 'create_group':
        if len(args) != 2:
            print 'create_group [group_name]'
            return

        headers = get_auth_headers()
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

        headers = get_auth_headers()
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
                'rm -rf /tmp/fabkit-repo/storage/* && '
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
            print 'upload [group_name] [file_name] [file_path]'
            return

        else:
            files = {'datafile': open(args[3], 'rb')}

            payload = {
                'name': args[2],
                'group': args[1],
            }

        headers = get_auth_headers()
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

        headers = get_auth_headers()
        download(headers, args[1], args[2], args[3])

    elif args[0] == 'setup':
        if len(args) != 1:
            print 'setup'
            return

        var_dir = CONF.client.package_var_dir
        if not os.path.exists(var_dir):
            os.makedirs(var_dir)
        fab_tar = '{0}/fabkit-repo.tar.gz'.format(var_dir)

        status, output = commands.getstatusoutput(
            'rm -rf {0}/fabkit-repo.tar.gz && rm -rf {0}/fabkit-repo'.format(
                var_dir, fab_tar))

        headers = get_auth_headers()
        download(headers, CONF.client.group, 'fabkit',
                 '{0}'.format(fab_tar))

        status, output = commands.getstatusoutput(
            'cd {0} && tar xf {1}'.format(
                var_dir, fab_tar))

        status, output = commands.getstatusoutput(
            'cp {0} {1}'.format(CONF._inifile, CONF._repo_dir))

        result_map = {}
        for cluster in CONF.client.clusters:
            for task in CONF.client.setup_task_patterns:
                fabcmd = '{0}/bin/fab -f {1}/fabfile node:{2},local manage:{3}'.format(
                    CONF.client.package_prefix, CONF._repo_dir, cluster, task)
                status, output = commands.getstatusoutput(fabcmd)

                print output

            pickle_file = '{0}/{1}/{2}/__cluster.pickle'.format(
                CONF._repo_dir, CONF.node_dir, cluster)
            with open(pickle_file) as f:
                cluster_data = pickle.load(f)
                result_map[cluster] = cluster_data['__status']['node_map'][CONF.host]

        print result_map
        return result_map

    elif args[0] == 'job':
        job_cluster = args[1]

        var_dir = CONF.client.package_var_dir
        if not os.path.exists(var_dir):
            os.makedirs(var_dir)
        fab_tar = '{0}/fabkit-repo.tar.gz'.format(var_dir)

        status, output = commands.getstatusoutput(
            'rm -rf {0}/fabkit-repo.tar.gz && rm -rf {0}/fabkit-repo'.format(
                var_dir, fab_tar))

        headers = get_auth_headers()
        download(headers, CONF.client.group, 'fabkit',
                 '{0}'.format(fab_tar))

        status, output = commands.getstatusoutput(
            'cd {0} && tar xf {1}'.format(
                var_dir, fab_tar))

        status, output = commands.getstatusoutput(
            'cp {0} {1}'.format(CONF._inifile, CONF._repo_dir))

        result_map = {}

        print '\n\nDEBUG job cluster'
        print job_cluster

        fabcmd = '{0}/bin/fab -f {1}/fabfile node:{2},yes job:local'.format(
            CONF.client.package_prefix, CONF._repo_dir, job_cluster)
        # status, output = commands.getstatusoutput(fabcmd)
        process = subprocess.Popen(fabcmd.split(' '), stdout=subprocess.PIPE)
        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)

        return result_map

        pickle_file = '{0}/{1}/{2}/__cluster.pickle'.format(
            CONF._repo_dir, CONF.node_dir, job_cluster)
        with open(pickle_file) as f:
            cluster_data = pickle.load(f)
            result_map[cluster] = cluster_data['__status']['node_map'][CONF.host]

        print result_map
        return result_map

    elif args[0] == 'check':
        if len(args) != 1:
            return

        var_dir = CONF.client.package_var_dir
        fab_tar = '{0}/fabkit-repo.tar.gz'.format(var_dir)

        result_map = {}
        for cluster in CONF.client.clusters:
            fabcmd = '{0}/bin/fab -f {1}/fabfile node:{2},local check'.format(
                CONF.client.package_prefix, CONF._repo_dir, cluster)
            status, output = commands.getstatusoutput(fabcmd)

            print output

            pickle_file = '{0}/{1}/{2}/__cluster.pickle'.format(
                CONF._repo_dir, CONF.node_dir, cluster)
            with open(pickle_file) as f:
                cluster_data = pickle.load(f)
                result_map[cluster] = cluster_data['__status']['node_map'][CONF.host]

        return result_map
