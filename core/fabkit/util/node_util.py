# coding: utf-8

import os
import yaml
import json
import pickle
import re
from copy import deepcopy
from fabkit import env, status, log
from host_util import get_expanded_hosts
from data_util import decode_data
from types import ListType, StringType
from oslo_config import cfg

CONF = cfg.CONF
RE_UPTIME = re.compile('^.*up (.+),.*user.*$')


def dict_merge(src_dict, data):
    if CONF.dict_merge_style == 'nested':
        return nested_merge(src_dict, data)
    if CONF.dict_merge_style == 'update':
        src_dict.update(data)
        return src_dict


def nested_merge(src_dict, data):
    if not isinstance(data, dict):
        return data

    result = deepcopy(src_dict)
    for k, v in data.iteritems():
        if k in result and isinstance(result[k], dict):
            result[k] = nested_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def update_host_script_map(tmp_hosts, fabscript, fabscript_kwargs):
    for host in tmp_hosts:
        script_map = env.host_script_map.get(host, {})
        script_var = script_map.get(fabscript, {})
        script_var = nested_merge(script_var, fabscript_kwargs)
        script_map[fabscript] = script_var
        env.host_script_map[host] = script_map


def include_cluster(cluster_name):
    data = {}
    cluster_dir = os.path.join(CONF._node_dir, cluster_name)
    for root, dirs, files in os.walk(cluster_dir):
        # load cluster data from yaml files
        for file in files:
            if file.find(CONF._yaml_extension) > -1:
                with open(os.path.join(root, file), 'r') as f:
                    load_data = yaml.load(f)

                    include_list = load_data.get('include', [])
                    if type(include_list) is ListType:
                        for cluster in include_list:
                            data = dict_merge(data, include_cluster(cluster))
                    elif type(include_list) is StringType:
                        data = dict_merge(data, include_cluster(include_list))

                    data = dict_merge(data, load_data)

        break

    return data


def _create_tmp_cluster_dir(cluster_dir, hosts, fabruns, cluster_data):
    if not os.path.exists(cluster_dir):
        os.makedirs(cluster_dir)

    data = {
        'node_map': {
            'tmp_node': {
                'hosts': [hosts],
                'fabruns': [fabruns],
            }
        }
    }
    if cluster_data is not None:
        tmp_data = json.loads(cluster_data)
        data.update(tmp_data)

    node_yml = os.path.join(cluster_dir, 'node.yml')
    with open(node_yml, 'w') as f:
        f.write(yaml.dump(data))


def load_runs(query, find_depth=1, use_tmp_node=False, fubruns=None, cluster_data=None):
    """ queryに基づいて、nodeを読み込む

    env.runs にクラスタごとの実行タスクリスト
    env.cluster_mapにクラスタごとのデータ情報を格納

    """
    env.host_script_map = {}

    # query rule
    # <cluster_name>/<node_search_pattern>
    is_contain_candidates = True
    splited_query = query.rsplit('/', 1)
    cluster_name = splited_query[0]
    if len(splited_query) > 1 and splited_query[1]:
        host_pattern = splited_query[1]
        if host_pattern.find('!') == 0:
            is_contain_candidates = False
            host_pattern = host_pattern[1:]
        candidates = [re.compile(c.replace('*', '.*')) for c in get_expanded_hosts(host_pattern)]
    else:
        host_pattern = ''
        candidates = None

    if use_tmp_node:
        cluster_dir = os.path.join(CONF._tmp_node_dir, cluster_name)
        _create_tmp_cluster_dir(cluster_dir, cluster_name, fubruns, cluster_data)
    else:
        cluster_dir = os.path.join(CONF._node_dir, cluster_name)

    # load cluster data from node dir
    runs = []
    depth = 1
    for root, dirs, files in os.walk(CONF._node_dir):
        if root.find(cluster_dir) == -1:
            continue

        # load cluster
        cluster_name = root.split(CONF._node_dir)[1]
        if cluster_name.find('/') == 0:
            cluster_name = cluster_name[1:]

        # default cluster dict
        cluster = {
            'name': cluster_name,
            'host_pattern': host_pattern,
            '__status': {
                'node_map': {},
                'fabscript_map': {},
            },
        }

        cluster.update(include_cluster(cluster_name))

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
                node_host = decode_data(node_host)
                if type(node_host) is ListType:
                    for tmp_node_host in node_host:
                        tmp_hosts.extend(get_expanded_hosts(tmp_node_host))
                else:
                    tmp_hosts.extend(get_expanded_hosts(node_host))

            cluster_node['hosts'] = tmp_hosts

            for tmp_fabscript in cluster_node['fabruns']:
                # fabruns = [<cluster>/<python_mod_path>, <cluster>/<python_mod_path>]
                fabscript = tmp_fabscript
                fabscript_kwargs = {}
                if isinstance(tmp_fabscript, dict):
                    for f, kwargs in tmp_fabscript.items():
                        fabscript = f
                        fabscript_kwargs = kwargs
                        break

                    update_host_script_map(tmp_hosts, fabscript, fabscript_kwargs)

                # fabscriptは、クラスタ単位で管理する
                fabscript_cluster = fabscript.rsplit('/', 1)[0]
                fabscript_mod = fabscript.rsplit('/', 1)[1]

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
                        'fabscript_kwargs': fabscript_kwargs,
                        'hosts': [],
                        'status_flow': [0],
                        'require': {},
                        'required': [],
                    }
                    fabscript_file = os.path.join(CONF._fabscript_module_dir,
                                                  fabscript_cluster, CONF._fabscript_yaml)
                    if os.path.exists(fabscript_file):
                        with open(fabscript_file, 'r') as f:
                            tmp_data = yaml.load(f)
                            fabscript_data.update(tmp_data.get(fabscript_mod, {}))

                    tmp_fabscript_map[fabscript] = fabscript_data

                tmp_fabscript_map[fabscript]['hosts'].extend(tmp_hosts)
                tmp_fabscript_map[fabscript]['env'] = cluster_node.get('env', {})

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
                    is_match = False
                    for candidate in candidates:
                        if candidate.search(host):
                            is_match = True
                            break
                    if is_match and not is_contain_candidates:
                        continue
                    elif not is_match and is_contain_candidates:
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
    if os.path.exists(CONF._node_meta_pickle):
        with open(CONF._node_meta_pickle) as f:
            node_meta = pickle.load(f)
    else:
        node_meta = {
            'recent_clusters': [],
        }

    recent_clusters = node_meta['recent_clusters']

    for cluster_name, data in env.cluster_map.items():
        node_status_map = data['__status'].pop('node_map')
        data['__status']['node_map'] = node_status_map

        status_yaml = os.path.join(CONF._node_dir, cluster_name, CONF._cluster_yaml)
        status_pickle = os.path.join(CONF._node_dir, cluster_name, CONF._cluster_pickle)
        status_data = {'__status': data['__status']}
        with open(status_yaml, 'w') as f:
            f.write(yaml.dump(status_data))
        with open(status_pickle, 'w') as f:
            pickle.dump(status_data, f)

        try:
            cluster_index = recent_clusters.index(cluster_name)
            del(recent_clusters[cluster_index])
        except ValueError:
            last_index = len(recent_clusters) - 1
            max_index = CONF.max_recent_clusters - 1
            if last_index == max_index:
                del(recent_clusters[last_index])
        recent_clusters.insert(0, cluster_name)

    node_meta['recent_clusters'] = recent_clusters
    with open(CONF._node_meta_pickle, 'w') as f:
        pickle.dump(node_meta, f)
