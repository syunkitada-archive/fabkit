# coding: utf-8

import yaml
import os
import json
from appconf import settings
from django.http import HttpResponse
from django.shortcuts import render
from apps.node.models import Node, NodeCluster
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
                        data = json.load(f)
                        datamap[data['name']] = data

    node_cluster['datamap'] = datamap
    node_cluster = json.dumps(node_cluster)

    context = {
        'title': 'Node List',
        'node_cluster': node_cluster,
        'node_clusters': node_clusters,
        'datamap': datamap,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'node/content.html', context)

    return render(request, 'node/index.html', context)


@login_required
def remove(request):
    if request.method == 'POST':
        targets = request.POST.getlist('target')
        clusters = set()
        for target in targets:
            node = Node.objects.get(pk=target)
            clusters.add(node.cluster.pk)
            node.is_deleted = True
            node.save()

        for cluster in clusters:
            node_count = Node.objects.filter(cluster=cluster, is_deleted=False).count()
            if node_count == 0:
                node_cluster = NodeCluster.objects.get(pk=cluster)
                node_cluster.is_deleted = True
                node_cluster.save()

        result = {
            'status': True,
        }

    else:
        result = {
            'status': True,
        }

    return HttpResponse(json.dumps(result))
