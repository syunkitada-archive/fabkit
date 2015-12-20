# coding: utf-8

import yaml
import commands
import re
import os
from fabkit import env
from oslo_config import cfg

CONF = cfg.CONF


def load_cluster(cluster_name=None):
    if not cluster_name:
        return

    if cluster_name not in env.cluster_map:
        RE_CLUSTER_YAML = re.compile('(.*\.yaml)'.format(CONF._node_dir))
        cluster_dir = os.path.join(CONF._node_dir, cluster_name)
        cmd = 'find {0} -maxdepth 1 -name "__*.yaml"'.format(cluster_dir)
        finded_cluster = commands.getoutput(cmd)

        cluster_yamls = set(RE_CLUSTER_YAML.findall(finded_cluster))
        cluster = {}
        for cluster_yaml in cluster_yamls:
            with open(cluster_yaml, 'r') as f:
                cluster.update(yaml.load(f.read()))

        env.cluster_map[cluster_name] = cluster
