# coding: utf-8

import pickle
import yaml
import os
import json
from markdown import markdown
from web_conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request, cluster=None):
    node_clusters = []
    for root, dirs, files in os.walk(settings.NODE_DIR):
        cluster_name = root.split(settings.NODE_DIR)
        cluster_yaml = os.path.join(root, '__cluster.yml')
        if os.path.exists(cluster_yaml):
            cluster_name = cluster_name[1][1:]
            node_clusters.append(cluster_name)

    node_clusters.sort()
    node_clusters.insert(0, 'recent')

    node_cluster = {}
    datamap = {}
    readme_html = ''

    with open(settings.NODE_META_PICKLE) as f:
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
        cluster = recent_clusters[index]

    cluster_dir = os.path.join(settings.NODE_DIR, cluster)
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
            readme_html = markdown(f.read(), extensions=['gfm'])

    node_cluster['datamap'] = datamap
    print node_cluster
    fabscript_map = node_cluster['__status']['fabscript_map']
    for fabscript_name, fabscript in fabscript_map.items():
        splited_name = fabscript_name.rsplit('/', 1)
        fabscript_cluster = splited_name[0]
        script = splited_name[1]
        fabscript_yaml = os.path.join(
            settings.FABSCRIPT_MODULE, fabscript_cluster, '__fabscript.yml')
        if os.path.exists(fabscript_yaml):
            with open(fabscript_yaml, 'r') as f:
                data = yaml.load(f)
                if data is not None:
                    fabscript.update(data.get(script, {}))

    node_clusters = json.dumps(node_clusters)
    node_cluster = json.dumps(node_cluster)

    context = {
        'title': 'Node List',
        'node_clusters': node_clusters,
        'node_cluster': node_cluster,
        'datamap': datamap,
        'readme_html': readme_html,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'node/content.html', context)

    return render(request, 'node/index.html', context)
