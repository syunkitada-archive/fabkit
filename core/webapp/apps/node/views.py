# coding: utf-8

import json
from django.http import HttpResponse
from django.shortcuts import render
from apps.node.models import Node, NodeCluster
from apps.fabscript.models import Fabscript
from django.core import serializers
from django.contrib.auth.decorators import login_required


@login_required
def index(request, cluster=None):
    if cluster:
        if int(cluster) == 0:
            nodes = serializers.serialize(
                'json',
                Node.objects.filter(cluster=None, is_deleted=False).order_by('-status', 'updated_at').all())
        else:
            nodes = serializers.serialize(
                'json',
                Node.objects.filter(cluster=cluster, is_deleted=False).order_by('-status', 'updated_at').all())
    else:
        nodes = serializers.serialize(
            'json',
            Node.objects.order_by('-status', 'updated_at').filter(is_deleted=False).all()[:50])

    node_clusters = serializers.serialize(
        'json', NodeCluster.objects.filter(is_deleted=False).order_by('name'))
    fabscripts = serializers.serialize('json', Fabscript.objects.all())
    context = {
        'title': 'Node List',
        'nodes': nodes,
        'node_clusters': node_clusters,
        'fabscripts': fabscripts,
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
            node_count = Node.objects.filter(cluster=cluster).count()
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
