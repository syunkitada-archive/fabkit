# coding: utf-8
from fabric.api import env
import re
import commands
import json
import datetime
import os
from types import StringType
from lib import conf
from lib import log
from lib.api import *  # noqa


def get_expanded_hosts(host=None):
    if not host or type(host) is not StringType:
        return []

    hosts = []
    start = host.find('[') + 1
    if start == 0:
        return [host]

    end = host.index(']', start)
    target = host[start:end]
    patterns = target.split('+')
    fragments = []
    for pattern in patterns:
        fragment = pattern.split('-')
        if len(fragment) == 2:
            length = len(fragment[0])
            length1 = len(fragment[1])
            if length < length1:
                length = length1

            fragment_start = int(fragment[0])
            fragment_end = int(fragment[1])
            while fragment_start <= fragment_end:
                format_str = '%0' + str(length) + 'd'
                fragments.append(format_str % fragment_start)
                fragment_start += 1
        else:
            fragments.append(fragment[0])

    head_host = host[:start-1]
    tail_host = host[end+1:]
    for fragment in fragments:
        host = head_host + fragment + tail_host
        hosts.extend(get_expanded_hosts(host))

    return hosts


def get_available_hosts(host_pattern=None):
    if not host_pattern or type(host_pattern) is not StringType:
        return []

    hosts = set()
    candidates = get_expanded_hosts(host_pattern)
    RE_NODE_JSON = re.compile('%s/(.*).json' % conf.NODE_DIR)
    for candidate in candidates:
        dir_file = candidate.rsplit('/', 1)
        if len(dir_file) > 1:
            node_dir = os.path.join(conf.NODE_DIR, dir_file[0])
            candidate = dir_file[1]
        else:
            node_dir = conf.NODE_DIR

        cmd = 'find %s -maxdepth 1 -name %s.json' % (node_dir, candidate)
        host_jsons = commands.getoutput(cmd)
        hosts.update(set(RE_NODE_JSON.findall(host_jsons)))

    return hosts


def load_json(host=None):
    if not host:
        host = env.host_attrs.get(env.host)
        host = host.get('hostpath')

    node_json = load_node_json(host)
    node_json.update(load_node_log_json(host))
    return node_json


def load_node_json(host=None):
    if not host:
        host = env.host_attrs.get(env.host).get('hostpath')

    path = get_node_json_file(host)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)

    return conf.get_initial_json(host)


def load_node_log_json(host=None):
    if not host:
        host = env.host_attrs.get(env.host).get('hostpath')

    path = log.get_node_log_json_file(host)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)

    return {}


def dump_json(dict_obj, host=None):
    if not host:
        host = env.host_attrs.get(env.host).get('hostpath')

    if host is not None:
        if not env.is_chef:
            node_file = get_node_json_file(host)
            # create dir
            dir_file = node_file.rsplit('/', 1)
            if len(dir_file) > 1 and not os.path.exists(dir_file[0]):
                os.makedirs(dir_file[0])
            with open(node_file, 'w') as f:
                json.dump(conf.get_node_json(dict_obj), f, sort_keys=True, indent=4)

        # create dir
        node_log_file = log.get_node_log_json_file(host)

        with open(node_log_file, 'w') as f:
            json.dump(conf.get_node_log_json(dict_obj), f, sort_keys=True, indent=4)


def get_node_json_file(host=None):
    return os.path.join(conf.NODE_DIR, '{0}.json'.format(host))


def remove_json(host=None):
    if not host:
        host = env.host
    path = '%s/%s.json' % (conf.NODE_DIR, host)
    os.remove(path)


def exists_json(host=None):
    if not host:
        host = env.host
    path = '%s/%s.json' % (conf.NODE_DIR, host)
    return os.path.exists(path)


def get_timestamp():
    today = datetime.datetime.today()
    return today.strftime('%Y-%m-%d %H:%M:%S')


def confirm(msg_ask, msg_cancel=None):
    if env.is_test:
        return True
    if raw_input('\n%s (y/n) ' % msg_ask) == 'y':
        return True
    else:
        if msg_cancel:
            print msg_cancel
        return False


def get_data_bag(bagname, itemname):
    if env.is_chef:
        result = cmd('knife data bag show %s %s -F json' % (bagname, itemname), True)
    else:
        result = cmd('knife solo data bag show %s %s -F json' % (bagname, itemname), True)
    if result[0] == 0:
        data_bag = json.loads(result[1])
        return data_bag
    else:
        return None
