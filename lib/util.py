# coding: utf-8
from fabric.api import env
import re, commands, json, datetime, os
from types import *
import conf

def expand_hostname(hostname=None):
    if not hostname or type(hostname) is not StringType:
        return []

    hostnames = []
    start = hostname.find('[') + 1
    if start == 0:
        return [hostname]

    end = hostname.index(']', start)
    target = hostname[start:end]
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

    head_hostname = hostname[:start-1]
    tail_hostname = hostname[end+1:]
    for fragment in fragments:
        hostname = head_hostname + fragment + tail_hostname
        hostnames.extend(expand_hostname(hostname))

    return hostnames

def get_available_hosts(host_pattern=None):
    if not host_pattern or type(host_pattern) is not StringType:
        return []

    hosts = set()
    candidates = expand_hostname(host_pattern)
    prog = re.compile('%s/(.*).json' % conf.node_path)
    for candidate in candidates:
        host_jsons = commands.getoutput('find %s/ -name %s.json' % (conf.node_path, candidate))
        hosts.update(set(prog.findall(host_jsons)))
    return hosts

def load_json(hostname=None):
    if not hostname:
        hostname = env.host
    path = '%s/%s.json' % (conf.node_path, hostname)
    with open(path, 'r') as f:
        return json.load(f)

def dump_json(dict_obj, hostname=None):
    if not hostname:
        hostname = env.host
    path = '%s/%s.json' % (conf.node_path, hostname)
    print path
    with open(path, 'w') as f:
        json.dump(dict_obj, f)

def remove_json(hostname=None):
    if not hostname:
        hostname = env.host
    path = '%s/%s.json' % (conf.node_path, hostname)
    os.remove(path)

def exists_json(hostname=None):
    if not hostname:
        hostname = env.host
    path = '%s/%s.json' % (conf.node_path, hostname)
    return os.path.exists(path)

def get_timestamp():
    today = datetime.datetime.today()
    return today.strftime('%Y-%m-%d %H:%M:%S')
