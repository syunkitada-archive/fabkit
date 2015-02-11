# coding: utf-8

import time
import os
import yaml
import re
from fabkit import conf, env, status
from host_util import get_expanded_hosts
from cluster_util import load_cluster
from fabscript_util import load_fabscript


RE_UPTIME = re.compile('^.*up (.+),.*user.*$')


def get_node_file(host=None):
    return os.path.join(conf.NODE_DIR, '{0}.yaml'.format(host))


def exists_node(host=None):
    if not host:
        host = env.host

    return os.path.exists(get_node_file(host))


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

        # load_cluster
        cluster_name = root.split(conf.NODE_DIR)[1]
        if cluster_name.find('/') == 0:
            cluster_name = cluster_name[1:]

        # default cluster dict
        cluster = {
            '__status': {
                'node_map': {},
                'fabscript_map': {},
            },
        }
        # load cluster data files
        for file in files:
            with open(os.path.join(root, file), 'r') as f:
                data = yaml.load(f)
                cluster.update(data)

        # node_map is definition of nodes in cluster
        cluster_node_map = cluster.get('node_map', {})
        # status is setup status of cluster
        cluster_status = cluster['__status']
        # status of nodes
        status_node_map = cluster_status['node_map']
        # status of fabscripts
        status_fabscript_map = cluster_status['fabscript_map']

        # expand hosts of node_map, and load fabscript of node
        tmp_fabscript_map = {}
        for role, cluster_node in cluster_node_map.items():
            node_hosts = cluster_node['hosts']

            tmp_hosts = []
            for node_host in node_hosts:
                tmp_hosts.extend(get_expanded_hosts(node_host))

            cluster_node['hosts'] = tmp_hosts

            for fabrun in cluster_node['fabruns']:
                if fabrun not in tmp_fabscript_map:
                    status.register_fabscript(status_fabscript_map, fabrun)

                    fabscript_data = status.get_default_fabscript_data(fabrun)
                    root_mod, mod = fabrun.rsplit('.', 1)
                    root_mod_file = os.path.join(conf.FABSCRIPT_MODULE_DIR,
                                                 root_mod.replace('.', '/'), '__fabscript__.yaml')
                    if os.path.exists(root_mod_file):
                        with open(root_mod_file, 'r') as f:
                            tmp_data = yaml.load(f)
                            fabscript_data.update(tmp_data.get(mod, {}))

                    tmp_fabscript_map[fabrun] = fabscript_data

                tmp_fabscript_map[fabrun]['hosts'].extend(tmp_hosts)

        cluster_status['fabscript_map'] = status_fabscript_map

        # tmp_fabscript_map を解析して、スクリプトの実行順序を組み立てる
        # 実行順序はcluster_runsに配列として格納する
        cluster_runs = []

        # スクリプトの依存関係を再帰的に求める
        def resolve_require(fabscript, data):
            for require_script, require_status in data['require'].items():
                require = tmp_fabscript_map.get(require_script)
                if require:
                    require['required'].append(fabscript)
                    if (require['require']) > 0:
                        resolve_require(fabscript, require)
                else:
                    require = status_fabscript_map.get(require_script)
                    if require:
                        if require['status'] == require_status and require['task_status'] == 0:
                            return

                    print 'Require Error\nCluster: {0}\nFabscript: {1} require {2}:{3}'.format(
                        cluster_name, fabscript, require_script, require_status)
                    exit()

        for fabscript, data in tmp_fabscript_map.items():
            resolve_require(fabscript, data)

        # スクリプト同士の依存関係が求められたので、これを使って正しい実行順序を組立てる
        for fabscript, data in tmp_fabscript_map.items():
            index = len(cluster_runs)

            for required in data['required']:
                for i, run in enumerate(cluster_runs):
                    if run['name'] == required:
                        if i < index:
                            index = i

            # セットアップの対象となるノードの初期化
            tmp_hosts = []
            for host in data['hosts']:
                if candidates:
                    for candidate in candidates:
                        if candidate.search(host):
                            break
                    else:
                        continue

                status.register_node(status_node_map, host, fabscript)
                tmp_hosts.append(host)

            data['hosts'] = tmp_hosts
            cluster_status['node_map'] = status_node_map
            fabscript_status = status_fabscript_map[fabscript]

            for flow in data['status_flow']:
                if fabscript_status < flow or flow == data['status_flow'][-1]:
                    tmp_data = data.copy()
                    tmp_data['expected_status'] = flow
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

        # end load_cluster

    env.runs = runs


def dump_cluster():
    # print env.cluster
    # TODO dump cluster
    print 'TODO dump cluster'


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
