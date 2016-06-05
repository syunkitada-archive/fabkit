# coding: utf-8

import pickle
import yaml
import os
import json
from web_apps.chat.utils import get_comments, get_cluster
from markdown import markdown
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from oslo_config import cfg
from web_lib import util

CONF = cfg.CONF


@login_required
def index(request, cluster=None):
    node_clusters = []
    for root, dirs, files in os.walk(CONF._node_dir):
        cluster_name = root.split(CONF._node_dir)
        cluster_yaml = os.path.join(root, '__cluster.yml')
        if os.path.exists(cluster_yaml):
            cluster_name = cluster_name[1][1:]
            node_clusters.append(cluster_name)

    node_clusters.sort()
    node_clusters.insert(0, 'recent')

    node_cluster = {}
    datamap = {}
    readme_html = ''

    with open(CONF._node_meta_pickle) as f:
        node_meta = pickle.load(f)

    recent_clusters = node_meta['recent_clusters']
    for index, cl in enumerate(recent_clusters):
        cl = cl.replace('/', '__')
        node_cluster = 'recent/{0}__{1}'.format(index, cl)
        node_clusters.append(node_cluster)

    if not cluster:
        cluster = 'recent/0'
    splited_cluster = cluster.split('/')
    if splited_cluster[0] == 'recent':
        if len(splited_cluster) == 1:
            index = 0
        else:
            index = int(splited_cluster[1])
        if len(recent_clusters) > 0:
            cluster = recent_clusters[index]
        else:
            context = {
                'cluster': None,
                'title': 'Node List: No Data',
            }
            return render(request, 'node/index.html', context)

    cluster_dir = os.path.join(CONF._node_dir, cluster)
    cluster_yaml = os.path.join(cluster_dir, '__cluster.yml')
    cluster_pickle = os.path.join(cluster_dir, '__cluster.pickle')
    datamap_dir = os.path.join(cluster_dir, 'datamap')

    if os.path.exists(cluster_pickle):
        with open(cluster_pickle) as f:
            node_cluster = pickle.load(f)
    elif os.path.exists(cluster_yaml):
        with open(cluster_yaml) as f:
            node_cluster = yaml.load(f)
        with open(cluster_pickle, 'w') as f:
            pickle.dump(node_cluster, f)

    if os.path.exists(datamap_dir):
        for root, dirs, files in os.walk(datamap_dir):
            for file in files:
                file = os.path.join(root, file)
                with open(file, 'r') as f:
                    data = yaml.load(f)
                    datamap[data['name']] = data

    readme = os.path.join(cluster_dir, 'README.md')
    if os.path.exists(readme):
        with open(readme) as f:
            readme_html = f.read()

    node_cluster['datamap'] = datamap

    fabscript_map = node_cluster['__status']['fabscript_map']
    util.update_fabscript_map(fabscript_map)
    print fabscript_map

    node_clusters = json.dumps(node_clusters)
    node_cluster = json.dumps(node_cluster)

    context = {
        'cluster': cluster,
        'title': 'Node: {0}'.format(cluster),
        'node_clusters': node_clusters,
        'node_cluster': node_cluster,
        'datamap': datamap,
        'readme_html': readme_html,
        'comments': get_comments(get_cluster(cluster)),
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'node/content.html', context)

    return render(request, 'node/index.html', context)
