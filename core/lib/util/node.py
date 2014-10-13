# coding: utf-8
from fabric.api import env
# import json
import yaml
from lib import log
from lib.api import *  # noqa
from host import *  # noqa
import re


RE_UPTIME = re.compile('^.*up (.+),.*user.*$')


def get_node_file(host=None):
    return os.path.join(conf.NODE_DIR, '{0}.yaml'.format(host))


def exists_node(host=None):
    if not host:
        host = env.host

    return os.path.exists(get_node_file(host))


def dump_node(host=None, node=None, is_init=False):
    if not host:
        host = env.host
        if host is None:
            raise Exception('Target host is None')

    if is_init:
        node_path = host
        node = convert_node()
    elif not node:
        node = env.node_map.get(host)
        node_path = node.get('path')
        node = convert_node(node)
    else:
        node_path = node.get('path')

    if not env.is_chef:
        node_file = get_node_file(node_path)

        # create dir
        splited_node_file = node_file.rsplit('/', 1)
        if len(splited_node_file) > 1 and not os.path.exists(splited_node_file[0]):
            os.makedirs(splited_node_file[0])

        with open(node_file, 'w') as f:
            f.write(yaml.dump(node))

    node_log_file = log.get_node_log_file(host)

    with open(node_log_file, 'w') as f:
        f.write(yaml.dump(convert_node_log(node)))


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

        node.update({'path': node_path})

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
            format_str = '{host:<' + str(max_len_host) + '} {fabrun_list}'

        horizontal_line = '-' * (max_len_host + 30)
        print horizontal_line
        print format_str.format(host='host',
                                run_list='run_list',
                                fabrun_list='fabrun_list',)
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
host_info     : {host_info}
uptime        : {uptime}
fabrun_list  : {fabrun_list}
last_fabcooks : {last_fabcooks}
last_check    : {last_check}
'''
            horizontal_line = '-' * 85
            print horizontal_line
            format_str += horizontal_line

    nodes = sorted(node_map.items(), reverse=False)

    for node_tapple in nodes:
        node = node_tapple[1]
        host = node.get('path', '')
        run_list = node.get('run_list', [])
        fabrun_list = node.get('fabrun_list', [])

        if not is_verbose:
            print format_str.format(host=host,
                                    run_list=run_list,
                                    fabrun_list=fabrun_list,)
        else:
            host_info = '{0}({1}) ssh:{2}'.format(host,
                                                  node.get('ipaddress', ''), node.get('ssh'))
            uptime = node.get('uptime', '')
            environment = node.get('chef_environment', '')
            last_cook = node.get('last_cook', '')
            last_fabcooks = node.get('last_fabcooks', [])
            last_runs = node.get('last_runs', [])
            last_check = node.get('last_check', '')
            print format_str.format(environment=environment,
                                    host_info=host_info,
                                    run_list=run_list,
                                    fabrun_list=fabrun_list,
                                    uptime=uptime,
                                    last_cook=last_cook,
                                    last_fabcooks=last_fabcooks,
                                    last_runs=last_runs,
                                    last_check=last_check,)


def convert_node(node={}):
    return {
        'fabrun_list': node.get('fabrun_list', []),
        'attr': node.get('data', {}),
    }


def convert_node_log(node={}):
    return {
        'ipaddress': node.get('ipaddress', ''),
        'last_check': node.get('last_check', ''),
        'last_cook': node.get('last_cook', ''),
        'last_fabcooks': node.get('last_fabcooks', []),
        'ssh': node.get('ssh', ''),
        'uptime': node.get('uptime', ''),
    }
