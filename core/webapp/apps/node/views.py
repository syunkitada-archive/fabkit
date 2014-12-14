# coding: utf-8

from django.shortcuts import render
from apps.node.models import Node


def index(request):
    nodes = Node.objects.all()
    context = {
        'title': 'Node List',
        'nodes': nodes,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'node/content.html', context)

    return render(request, 'node/index.html', context)
