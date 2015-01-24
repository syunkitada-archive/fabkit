# coding: utf-8

import re
import os
import commands
from types import StringType
from fabkit import conf


def get_expanded_hosts(host=None, host_fragments=[]):
    ''' 与えられたホストパターンを展開してホストリストを返します。
    '''
    if not host or type(host) is not StringType:
        return []

    hosts = []
    start = host.find('[') + 1
    if start == 0:
        return [(host, host_fragments)]

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
        tmp_host_fragments = host_fragments + [fragment]
        hosts.extend(get_expanded_hosts(host, tmp_host_fragments))

    return hosts


def get_available_hosts(host_pattern=None):
    if not host_pattern or type(host_pattern) is not StringType:
        return []

    hosts = set()
    candidates = get_expanded_hosts(host_pattern)
    RE_NODE_JSON = re.compile('%s/(.*).yaml' % conf.NODE_DIR)
    for candidate in candidates:
        candidate = candidate[0]
        splited_candidate = candidate.rsplit('/', 1)
        if len(splited_candidate) > 1:
            node_dir = os.path.join(conf.NODE_DIR, splited_candidate[0])
            candidate = splited_candidate[1]
        else:
            node_dir = conf.NODE_DIR

        cmd = 'find %s -maxdepth 1 -name "%s.yaml"' % (node_dir, candidate)
        host_jsons = commands.getoutput(cmd)
        hosts.update(set(RE_NODE_JSON.findall(host_jsons)))

    return hosts
