# coding: utf-8

import time
import os
import yaml
import json
import re
from fabkit import conf, env, status, db
from host_util import get_available_hosts
from terminal import print_node_map
from cluster_util import load_cluster
from fabscript_util import load_fabscript


RE_UPTIME = re.compile('^.*up (.+),.*user.*$')


def get_node_file(host=None):
    return os.path.join(conf.NODE_DIR, '{0}.yaml'.format(host))


def exists_node(host=None):
    if not host:
        host = env.host

    return os.path.exists(get_node_file(host))


def dump_node(host_path=None, node=None, is_init=False):
    if not host_path:
        host_path = env.host
        if host_path is None:
            raise Exception('Target host is None')

    if is_init:
        node_path = host_path
        node = convert_node()
        node['path'] = node_path

        splited_host = node_path.rsplit('/', 1)
        if len(splited_host) > 1:
            host = splited_host[1]
            env.node_map[host] = node
        else:
            host = node_path

    elif not node:
        node = env.node_map.get(host_path)
        node_path = node.get('path')
        node = convert_node(node)
    else:
        node_path = node.get('path')
        node = convert_node(node)

    node_file = get_node_file(node_path)

    # create dir
    splited_node_file = node_file.rsplit('/', 1)
    if len(splited_node_file) > 1 and not os.path.exists(splited_node_file[0]):
        os.makedirs(splited_node_file[0])

    with open(node_file, 'w') as f:
        f.write(yaml.dump(node))


def load_node(host=None):
    if not host:
        return env.node_map.get(env.host)

    splited_host = host.rsplit('/', 1)
    if len(splited_host) > 1:
        node_path = host
        cluster = splited_host[0]
        host = splited_host[1]
    else:
        cluster = None
        node_path = host

    node_file = get_node_file(node_path)
    if os.path.exists(node_file):
        with open(node_file, 'r') as f:
            node = yaml.load(f)

        logs = []
        for fabscript in node['fabruns']:
            load_fabscript(fabscript)
            logs.append({
                'fabscript': fabscript,
                'status': status.FABSCRIPT_REGISTERED,
                'msg': 'registered',
                'timestamp': time.time(),
            })

        node.update({
            'cluster': cluster,
            'path': node_path,
            'logs': logs,
        })

        env.node_map.update({host: node})
        env.hosts.append(host)

        load_cluster(cluster)

        return node

    return {}


def load_node_map(host=None, find_depth=1):
    if not host:
        return env.host_map

    hosts = get_available_hosts(host, find_depth)
    for host in hosts:
        load_node(host)

    return env.node_map


def remove_node(host=None):
    if not host:
        return

    path = '%s/%s.yaml' % (conf.NODE_DIR, host)
    os.remove(path)


def update_log(fabscript, status, msg):
    node = env.node_map.get(env.host)
    tmp_logs = []
    for log in node['logs']:
        if log['fabscript'] == fabscript:
            log['status'] = status
            log['msg'] = msg
            log['timestamp'] = time.time()

        tmp_logs.append(log)

    node['logs'] = tmp_logs
    env.node_map[env.host] = node


def print_db_nodes(nodes=[], option=''):
    for node in nodes:
        print node


def convert_node(node={}):
    return {
        'fabruns': node.get('fabruns', []),
        'data': node.get('data', {}),
    }
