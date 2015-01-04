# coding: utf-8

import json
from django.http import HttpResponse
from django.shortcuts import render
from apps.node.models import Node, NodeCluster
from django.core import serializers
from django.contrib.auth.decorators import login_required


@login_required
def index(request, cluster=None):
    if cluster:
        if int(cluster) == 0:
            nodes = serializers.serialize(
                'json',
                Node.objects.filter(cluster=None).order_by('path').all())
        else:
            nodes = serializers.serialize(
                'json',
                Node.objects.filter(cluster=cluster).order_by('path').all())
    else:
        nodes = serializers.serialize('json', Node.objects.order_by('path').all()[:50])

    node_clusters = serializers.serialize('json', NodeCluster.objects.all().order_by('name'))
    context = {
        'title': 'Node List',
        'nodes': nodes,
        'node_clusters': node_clusters,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'node/content.html', context)

    return render(request, 'node/index.html', context)


@login_required
def remove(request):
    if request.method == 'POST':
        targets = request.POST.getlist('target')
        for target in targets:
            node = Node.objects.get(pk=target)
            node.delete()

        result = {
            'status': True,
        }

    else:
        result = {
            'status': True,
        }

    return HttpResponse(json.dumps(result))
