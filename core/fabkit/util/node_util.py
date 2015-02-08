# coding: utf-8

import time
import os
import yaml
import re
from fabkit import conf, env, status, db
from host_util import get_available_hosts, host_filter, get_expanded_hosts
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


def load_runs(query, find_depth=1):
    splited_query = query.rsplit('/', 1)
    cluster_name = splited_query[0]

    if len(splited_query) > 1 and splited_query[1]:
        host_pattern = splited_query[1]
        candidates = [re.compile(c.replace('*', '.*')) for c in get_expanded_hosts(host_pattern)]
    else:
        candidates = None

    cluster_dir = os.path.join(conf.NODE_DIR, cluster_name)

    runs = []
    depth = 1
    for root, dirs, files in os.walk(conf.NODE_DIR):
        if root.find(cluster_dir) == -1:
            continue

        cluster_name = root.split(conf.NODE_DIR)[1]
        cluster = {}
        for file in files:
            with open(os.path.join(root, file), 'r') as f:
                data = yaml.load(f)
                cluster.update(data)

        cluster_node_map = cluster.get('node_map', {})
        cluster_state_map = cluster.get('state', {})   # TODO __state__.yaml  # noqa
        cluster_node_state_map = cluster_state_map.get('node_map', {})  # noqa
        cluster_fabscript_map = cluster_state_map.get('fabscript_map', {})  # noqa
        tmp_fabscript_map = {}

        for role, cluster_node in cluster_node_map.items():
            node_hosts = cluster_node['hosts']

            tmp_hosts = []
            for node_host in node_hosts:
                tmp_hosts.extend(get_expanded_hosts(node_host))

            cluster_node['hosts'] = tmp_hosts

            for fabrun in cluster_node['fabruns']:
                if fabrun not in tmp_fabscript_map:
                    state = cluster_fabscript_map.get(fabrun, {}).get('state', 0)
                    task_state = cluster_fabscript_map.get(fabrun, {}).get('task_state', 0)
                    data = {
                        'name': fabrun,
                        'hosts': [],
                        'state': state,
                        'task_state': task_state,
                        'state_flow': [1],
                        'require': {},
                        'required': [],
                    }

                    root_mod, mod = fabrun.rsplit('.', 1)
                    root_mod_file = os.path.join(conf.FABSCRIPT_MODULE_DIR,
                                                 root_mod.replace('.', '/'), '__fabscript__.yaml')
                    if os.path.exists(root_mod_file):
                        with open(root_mod_file, 'r') as f:
                            tmp_data = yaml.load(f)
                            data.update(tmp_data.get(mod, {}))

                    tmp_fabscript_map[fabrun] = data

                tmp_fabscript_map[fabrun]['hosts'].extend(tmp_hosts)

        # runs
        cluster_runs = []

        def resolve_require(fabscript, data):
            for script, state in data['require'].items():
                require = tmp_fabscript_map.get(script)
                if require:
                    require['required'].append(fabscript)
                    if (require['require']) > 0:
                        resolve_require(fabscript, require)
                else:
                    require = cluster_fabscript_map.get(script)
                    if require:
                        if require['state'] == state and require['task_state'] == 0:
                            return

                    print 'Require Error\nCluster: {0}\nFabscript: {1} require {2}:{3}'.format(
                        cluster_name, fabscript, script, state)
                    exit()

        for fabscript, data in tmp_fabscript_map.items():
            resolve_require(fabscript, data)

        for fabscript, data in tmp_fabscript_map.items():
            index = len(cluster_runs)

            for required in data['required']:
                for i, run in enumerate(cluster_runs):
                    if run['name'] == required:
                        if i < index:
                            index = i

            tmp_hosts = {}
            for host in data['hosts']:
                if candidates:
                    for candidate in candidates:
                        if candidate.search(host):
                            break
                    else:
                        continue

                node = cluster_node_state_map.get(host, {})
                if fabscript not in node:
                    node[fabscript] = {
                        'state': 0,
                        'task_state': 0,
                    }

                    cluster_node_state_map[host] = node
                tmp_hosts[host] = node

            data['node_map'] = tmp_hosts

            for flow in data['state_flow']:
                if data['state'] < flow or flow == data['state_flow'][-1]:
                    tmp_data = data.copy()
                    tmp_data['expected_state'] = flow
                    cluster_runs.insert(index, tmp_data)
                    index += 1

        runs.append({
            'cluster': cluster_name,
            'runs': cluster_runs,
        })

        cluster['fabscript_map'] = tmp_fabscript_map
        env.cluster_map[cluster_name] = cluster

        depth += 1
        if depth > find_depth:
            break

    env.runs = runs


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
