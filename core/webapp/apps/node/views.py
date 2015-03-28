# coding: utf-8

import yaml
import os
import json
from markdown import markdown
from appconf import settings
from django.http import HttpResponse
from django.shortcuts import render
from apps.node.models import Node, NodeCluster
from django.contrib.auth.decorators import login_required


@login_required
def index(request, cluster=None):
    node_clusters = []
    readme_html = ''
    for root, dirs, files in os.walk(settings.NODE_DIR):
        cluster_name = root.split(settings.NODE_DIR)
        cluster_yaml = os.path.join(root, '__cluster.yml')
        if os.path.exists(cluster_yaml):
            cluster_name = cluster_name[1][1:]
            node_clusters.append(cluster_name)

        readme = os.path.join(root, 'README.md')
        if os.path.exists(readme):
            with open(readme) as f:
                readme_html = markdown(f.read())

    node_clusters.sort()
    node_clusters = json.dumps(node_clusters)

    node_cluster = {}
    datamap = {}
    if cluster is not None:
        cluster_dir = os.path.join(settings.NODE_DIR, cluster)
        cluster_yaml = os.path.join(cluster_dir, '__cluster.yml')
        datamap_dir = os.path.join(cluster_dir, 'datamap')
        if os.path.exists(cluster_yaml):
            with open(cluster_yaml) as f:
                node_cluster = yaml.load(f)
        if os.path.exists(datamap_dir):
            for root, dirs, files in os.walk(datamap_dir):
                for file in files:
                    file = os.path.join(root, file)
                    with open(file, 'r') as f:
                        data = yaml.load(f)
                        datamap[data['name']] = data

        node_cluster['datamap'] = datamap
        fabscript_map = node_cluster['__status']['fabscript_map']
        for fabscript_name, fabscript in fabscript_map.items():
            splited_name = fabscript_name.split('/')
            fabscript_cluster = splited_name[0]
            script = splited_name[1]
            fabscript_yaml = os.path.join(
                settings.FABSCRIPT_MODULE, fabscript_cluster, '__fabscript.yml')
            if os.path.exists(fabscript_yaml):
                with open(fabscript_yaml, 'r') as f:
                    data = yaml.load(f)
                    if data is not None:
                        fabscript.update(data.get(script, {}))

    node_cluster = json.dumps(node_cluster)

    context = {
        'title': 'Node List',
        'node_cluster': node_cluster,
        'node_clusters': node_clusters,
        'datamap': datamap,
        'readme_html': readme_html,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'node/content.html', context)

    return render(request, 'node/index.html', context)
