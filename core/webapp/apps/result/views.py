# coding: utf-8

from django.shortcuts import render
from django.core import serializers
from apps.result.models import Result


def index(request):
    results = serializers.serialize('json', Result.objects.all().order_by('node_path'))
    context = {
        'title': 'Result Log',
        'results': results,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'result/content.html', context)

    return render(request, 'result/index.html', context)
