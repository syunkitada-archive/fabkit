# coding: utf-8

import json
from django.http import HttpResponse
from django.shortcuts import render
from django.core import serializers
from apps.node.models import NodeCluster
from apps.result.models import Result
from apps.fabscript.models import Fabscript
from django.contrib.auth.decorators import login_required


@login_required
def index(request, cluster=None):
    if cluster:
        if int(cluster) == 0:
            results = serializers.serialize(
                'json',
                Result.objects.filter(cluster=None).order_by('-status', 'node_path').all())
        else:
            results = serializers.serialize(
                'json',
                Result.objects.filter(cluster=cluster).order_by('-status', 'node_path').all())
    else:
        results = serializers.serialize(
            'json',
            Result.objects.order_by('-status', '-updated_at').all()[:50])

    node_clusters = serializers.serialize('json', NodeCluster.objects.all())
    fabscripts = serializers.serialize('json', Fabscript.objects.all())
    context = {
        'title': 'Result Log',
        'results': results,
        'fabscripts': fabscripts,
        'node_clusters': node_clusters,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'result/content.html', context)

    return render(request, 'result/index.html', context)


@login_required
def remove(request):
    if request.method == 'POST':
        targets = request.POST.getlist('target')
        for target in targets:
            result = Result.objects.get(pk=target)
            result.delete()

        result = {
            'status': True,
        }

    else:
        result = {
            'status': True,
        }

    return HttpResponse(json.dumps(result))
