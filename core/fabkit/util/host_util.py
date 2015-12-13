# coding: utf-8

import re
import os
import commands
from types import StringType
from oslo_config import cfg

CONF = cfg.CONF


def get_expanded_hosts(host=None):
    ''' 与えられたホストパターンを展開してホストリストを返します。
    '''
    if not host or type(host) is not StringType:
        return []

    # start = host.find('!')
    # if start == 0:
    #     host_cmd = 'cd {0} && {1}'.format(conf.NODE_DIR, host[1:])
    #     hosts = commands.getoutput(host_cmd)
    #     hosts = hosts.split('\n')
    #     return hosts

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


def get_available_hosts(host_pattern=None, find_depth=1):
    if not host_pattern or type(host_pattern) is not StringType:
        return []

    hosts = set()
    candidates = get_expanded_hosts(host_pattern)
    RE_NODE_YAML = re.compile('{0}/(.*).yaml'.format(CONF._node_dir))
    for candidate in candidates:
        candidate = candidate[0]
        splited_candidate = candidate.rsplit('/', 1)
        if len(splited_candidate) > 1:
            node_dir = os.path.join(CONF._node_dir, splited_candidate[0])
            candidate = splited_candidate[1]
        else:
            node_dir = CONF._node_dir

        cmd = 'find {0} -maxdepth {1} -name "{2}.yaml"'.format(node_dir, find_depth, candidate)
        host_jsons = commands.getoutput(cmd)
        hosts.update(set(RE_NODE_YAML.findall(host_jsons)))

    available_hosts = []
    for host in hosts:
        if host.find('__') == -1:
            available_hosts.append(host)

    return available_hosts


def host_filter(host, filters):
    if len(filters) == 0:
        return True

    else:
        is_match = False
        for f in filters:
            if re.search(f, host):
                is_match = True
            else:
                is_match = False
                break

        return is_match
