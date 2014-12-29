# coding: utf-8

import json
from django.http import HttpResponse
from django.shortcuts import render
from apps.node.models import Node
from django.core import serializers


def index(request):
    nodes = serializers.serialize('json', Node.objects.all().order_by('path'))
    context = {
        'title': 'Node List',
        'nodes': nodes,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'node/content.html', context)

    return render(request, 'node/index.html', context)


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
