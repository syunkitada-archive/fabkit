# coding: utf-8

import yaml
import json
import commands
import re
import os
from fabkit import conf, env
from apps.node.models import NodeCluster
from django.db import transaction


def get_cluster(cluster_name=None):
    if not cluster_name:
        return {}

    RE_CLUSTER_YAML = re.compile('(.*\.yaml)'.format(conf.NODE_DIR))
    cluster_dir = os.path.join(conf.NODE_DIR, cluster_name)
    cmd = 'find {0} -maxdepth 1 -name "__*.yaml"'.format(cluster_dir)
    finded_cluster = commands.getoutput(cmd)

    cluster_yamls = set(RE_CLUSTER_YAML.findall(finded_cluster))
    cluster = {}
    for cluster_yaml in cluster_yamls:
        with open(cluster_yaml, 'r') as f:
            cluster.update(yaml.load(f.read()))

    update_cluster(cluster_name, cluster)
    return cluster


def load_cluster(node):
    cluster_name = node['path'].rsplit('/', 1)[0]
    env.cluster = get_cluster(cluster_name)


@transaction.atomic
def update_cluster(name, data={}):
    try:
        cluster = NodeCluster.objects.get(name=name)
        if cluster.is_deleted:
            cluster.is_deleted = False
    except NodeCluster.DoesNotExist:
        cluster = NodeCluster(name=name)

    cluster.data = json.dumps(data)
    cluster.save()
