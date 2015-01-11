# coding: utf-8
from fabric.api import env
# import json
import yaml
import json
from lib.api import *  # noqa
from host import *  # noqa
import re
import time


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

        db.update_node(host)

    elif not node:
        node = env.node_map.get(host_path)
        db.update_node()
        node_path = node.get('path')
        node = convert_node(node)
    else:
        node_path = node.get('path')
        node = convert_node(node)

    if not env.is_chef:
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
        host = splited_host[1]
    else:
        node_path = host

    node_file = get_node_file(node_path)
    if os.path.exists(node_file):
        with open(node_file, 'r') as f:
            # return json.load(f)
            node = yaml.load(f)

        logs = []
        for fabrun in node['fabruns']:
            logs.append({
                'fabscript': fabrun,
                'status': -1,
                'msg': 'registered',
                'timestamp': time.time(),
            })

        node.update({
            'path': node_path,
            'logs': logs,
        })

        env.node_map.update({host: node})
        env.hosts.append(host)

        return node

    return {}


def load_node_map(host=None):
    if not host:
        return env.host_map

    hosts = get_available_hosts(host)
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


def print_node_map(node_map=None, option=None):
    if not node_map:
        node_map = env.node_map

    if len(node_map) == 0:
        max_len_host = 10
    else:
        max_len_host = max([len(node['path']) for node in node_map.values()])

    if env.is_chef:
        format_str = '{host:<' + str(max_len_host) + '} {run_list}'
    else:
        if option:
            format_str = '{host:<' + str(max_len_host) + '} {status:<6} {logs}'
        else:
            format_str = '{host:<' + str(max_len_host) + '} {fabruns}'

    horizontal_line = '-' * (max_len_host + 30)
    print horizontal_line
    print format_str.format(host='host',
                            run_list='run_list',
                            status='status',
                            logs='logs',
                            fabruns='fabruns',)
    print horizontal_line

    nodes = sorted(node_map.items(), reverse=False)

    for node_tapple in nodes:
        node = node_tapple[1]
        host = node.get('path', '')
        if option == 'status' or option == 'error':
            tmp_node = db.get_node(node)
            status = tmp_node.status
            if option == 'error' and status == 0:
                continue

            logs = ''
            tmp_logs = json.loads(tmp_node.logs)
            last_log_i = len(tmp_logs) - 1
            for i, log in enumerate(tmp_logs):
                if log['status'] != 0:
                    logs += '\033[93m{0[fabscript]}: {0[msg]} [{0[status]}]\033[0m'.format(log)
                else:
                    logs += '{0[fabscript]}: {0[msg]} [{0[status]}]'.format(log)
                if not i == last_log_i:
                    logs += '\n' + (' ' * (max_len_host + 8))

        else:
            status = ''
            logs = ''

        run_list = node.get('run_list', [])
        fabruns = node.get('fabruns', [])

        print format_str.format(host=host,
                                run_list=run_list,
                                status=status,
                                logs=logs,
                                fabruns=fabruns,
                                )


def print_db_nodes(nodes=[], option=''):
    for node in nodes:
        print node


def convert_node(node={}):
    return {
        'fabruns': node.get('fabruns', []),
        'data': node.get('data', {}),
    }
