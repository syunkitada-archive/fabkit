# coding: utf-8

from django.shortcuts import render
from apps.fabscript.models import Fabscript
from django.core import serializers


def index(request):
    fabscripts = serializers.serialize('json', Fabscript.objects.all())
    context = {
        'title': 'Fabscript List',
        'fabscripts': fabscripts,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'fabscript/content.html', context)

    return render(request, 'fabscript/index.html', context)
