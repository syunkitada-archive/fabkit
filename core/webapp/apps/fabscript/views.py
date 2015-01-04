# coding: utf-8

import json
from django.http import HttpResponse
from django.shortcuts import render
from apps.fabscript.models import Fabscript
from django.core import serializers
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    fabscripts = serializers.serialize('json', Fabscript.objects.all().order_by('name'))
    context = {
        'title': 'Fabscript List',
        'fabscripts': fabscripts,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'fabscript/content.html', context)

    return render(request, 'fabscript/index.html', context)


@login_required
def remove(request):
    if request.method == 'POST':
        targets = request.POST.getlist('target')
        for target in targets:
            fabscript = Fabscript.objects.get(pk=target)
            fabscript.delete()

        result = {
            'status': True,
        }

    else:
        result = {
            'status': True,
        }

    return HttpResponse(json.dumps(result))
