# coding: utf-8
from fabric.api import env
# import json
import yaml
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


def print_node_map(node_map=None, option=''):
    if not node_map:
        node_map = env.node_map

    is_verbose = False

    if option is not None and option.find('v') > -1:
        is_verbose = True

    if not is_verbose:
        if len(node_map) == 0:
            max_len_host = 10
        else:
            max_len_host = max([len(node['path']) for node in node_map.values()])
        if env.is_chef:
            format_str = '{host:<' + str(max_len_host) + '} {run_list}'
        else:
            format_str = '{host:<' + str(max_len_host) + '} {fabruns}'

        horizontal_line = '-' * (max_len_host + 30)
        print horizontal_line
        print format_str.format(host='host',
                                run_list='run_list',
                                fabruns='fabruns',)
        print horizontal_line

    else:
        if env.is_chef:
            format_str = '''\
host_info     : {host_info}
uptime        : {uptime}
environment   : {environment}
run_list      : {run_list}
last_cook     : {last_cook}
last_check    : {last_check}
'''
        else:
            format_str = '''\
host_info      : {host_info}
uptime         : {uptime}
fabruns        : {fabruns}
last_fabruns   : {last_fabruns}
fabrun_history : TODO
last_check     : {last_check}
'''
            horizontal_line = '-' * 85
            print horizontal_line
            format_str += horizontal_line

    nodes = sorted(node_map.items(), reverse=False)

    for node_tapple in nodes:
        node = node_tapple[1]
        host = node.get('path', '')
        run_list = node.get('run_list', [])
        fabruns = node.get('fabruns', [])

        if not is_verbose:
            print format_str.format(host=host,
                                    run_list=run_list,
                                    fabruns=fabruns,)
        else:
            host_info = '{0}({1}) ssh:{2}'.format(host,
                                                  node.get('ipaddress', ''), node.get('ssh'))
            uptime = node.get('uptime', '')
            environment = node.get('chef_environment', '')
            last_cook = node.get('last_cook', '')
            last_fabruns = node.get('last_fabruns', [])
            last_runs = node.get('last_runs', [])
            last_check = node.get('last_check', '')
            print format_str.format(environment=environment,
                                    host_info=host_info,
                                    run_list=run_list,
                                    fabruns=fabruns,
                                    uptime=uptime,
                                    last_cook=last_cook,
                                    last_fabruns=last_fabruns,
                                    last_runs=last_runs,
                                    last_check=last_check,)


def convert_node(node={}):
    return {
        'fabruns': node.get('fabruns', []),
        'data': node.get('data', {}),
    }
