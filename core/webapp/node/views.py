# coding: utf-8

from django.shortcuts import render
from node.models import Node


def index(request):
    nodes = Node.objects.all()
    return render(request, 'node/index.html', {'nodes': nodes})
