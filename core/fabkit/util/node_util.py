# coding: utf-8

import os
import yaml
import re
from fabkit import conf, env, status, log
from host_util import get_expanded_hosts


RE_UPTIME = re.compile('^.*up (.+),.*user.*$')


def load_runs(query, find_depth=1):
    """ queryに基づいて、nodeを読み込む

    env.runs にクラスタごとの実行タスクリスト
    env.cluster_mapにクラスタごとのデータ情報を格納

    """

    # query rule
    # <cluster_name>/<node_search_pattern>
    splited_query = query.rsplit('/', 1)
    cluster_name = splited_query[0]
    if len(splited_query) > 1 and splited_query[1]:
        host_pattern = splited_query[1]
        candidates = [re.compile(c.replace('*', '.*')) for c in get_expanded_hosts(host_pattern)]
    else:
        candidates = None

    cluster_dir = os.path.join(conf.NODE_DIR, cluster_name)

    # load cluster data from node dir
    runs = []
    depth = 1
    for root, dirs, files in os.walk(conf.NODE_DIR):
        if root.find(cluster_dir) == -1:
            continue

        # load cluster
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
        # load cluster data from yaml files
        for file in files:
            if file.find(conf.YAML_EXTENSION) > -1:
                with open(os.path.join(root, file), 'r') as f:
                    data = yaml.load(f)
                    cluster.update(data)

        # node_map is definition of nodes in cluster
        cluster_node_map = cluster.get('node_map', {})
        # status is setup status of cluster
        cluster_status = cluster['__status']
        # status of nodes
        node_status_map = cluster_status['node_map']
        # status of fabscripts
        fabscript_status_map = cluster_status['fabscript_map']

        # expand hosts of node_map, and load fabscript of node
        # tmp_fabscript_mapに実行候補のfabscriptをすべて格納する
        tmp_fabscript_map = {}
        for role, cluster_node in cluster_node_map.items():
            node_hosts = cluster_node['hosts']

            tmp_hosts = []
            for node_host in node_hosts:
                tmp_hosts.extend(get_expanded_hosts(node_host))

            cluster_node['hosts'] = tmp_hosts

            for fabscript in cluster_node['fabruns']:
                # fabruns = [<cluster>/<python_mod_path>, <cluster>/<python_mod_path>]
                # fabscriptは、クラスタ単位で管理する
                fabscript_cluster = fabscript.rsplit('/', 1)[0]
                fabscript_mod = fabscript.rsplit('/', 1)[1]
                fabscript = fabscript.replace('/', '.')  # モジュールとして読み込めるよう.ドット区切りに直す

                if fabscript not in tmp_fabscript_map:
                    if fabscript not in fabscript_status_map:
                        # このクラスタにおいて実行履歴のないfabscriptはデフォルト値を登録する
                        fabscript_status_map[fabscript] = {
                            'status': 0,
                            'task_status': status.REGISTERED,
                        }

                    # デフォルト値
                    fabscript_data = {
                        'fabscript': fabscript,
                        'hosts': [],
                        'status_flow': [0],
                        'require': {},
                        'required': [],
                    }
                    fabscript_file = os.path.join(conf.FABSCRIPT_MODULE_DIR,
                                                  fabscript_cluster, conf.FABSCRIPT_YAML)
                    if os.path.exists(fabscript_file):
                        with open(fabscript_file, 'r') as f:
                            tmp_data = yaml.load(f)
                            fabscript_data.update(tmp_data.get(fabscript_mod, {}))

                    tmp_fabscript_map[fabscript] = fabscript_data

                tmp_fabscript_map[fabscript]['hosts'].extend(tmp_hosts)

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
                    require = fabscript_status_map.get(require_script)
                    if require:
                        if require['status'] == require_status and require['task_status'] == 0:
                            return

                    log.error('Require Error\nCluster: {0}\nFabscript: {1} require {2}:{3}'.format(
                        cluster_name, fabscript, require_script, require_status))
                    exit()

        for fabscript, data in tmp_fabscript_map.items():
            resolve_require(fabscript, data)

        # スクリプト同士の依存関係が求められたので、これを使って正しい実行順序を組立てる
        for fabscript, data in tmp_fabscript_map.items():
            index = len(cluster_runs)

            for required in data['required']:
                for i, run in enumerate(cluster_runs):
                    if run['fabscript'] == required:
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

                tmp_hosts.append(host)
                node = node_status_map.get(host, {'fabscript_map': {}})
                if fabscript not in node['fabscript_map']:
                    node['fabscript_map'][fabscript] = {
                        'status': 0,
                        'check_status': -1,
                        'msg': '',
                        'check_msg': '',
                    }

                if env.is_setup:
                    node['fabscript_map'][fabscript].update({
                        'msg': status.REGISTERED_MSG,
                        'task_status': status.REGISTERED,
                    })
                elif env.is_check:
                    node['fabscript_map'][fabscript].update({
                        'check_msg': status.REGISTERED_MSG,
                        'task_status': status.REGISTERED,
                    })

                node_status_map[host] = node

            if len(tmp_hosts) > 0:
                fabscript_status_map[fabscript]['task_status'] = status.REGISTERED

            data['hosts'] = tmp_hosts
            cluster_status['node_map'] = node_status_map
            fabscript_status = fabscript_status_map[fabscript]['status']

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

        cluster_status['fabscript_map'] = fabscript_status_map

        cluster['fabscript_map'] = tmp_fabscript_map
        env.cluster_map[cluster_name] = cluster

        depth += 1
        if depth > find_depth:
            break

        # end load_cluster

    env.runs = runs

    log.debug('env.runs = {0}\n'.format(env.runs))
    log.debug('env.cluster_map = {0}\n'.format(env.cluster_map))


def dump_status():
    for cluster_name, data in env.cluster_map.items():
        node_status_map = data['__status'].pop('node_map')
        data['__status']['node_map'] = node_status_map

        status_yaml = os.path.join(conf.NODE_DIR, cluster_name, conf.CLUSTER_YAML)
        with open(status_yaml, 'w') as f:
            f.write(yaml.dump({'__status': data['__status']}))
