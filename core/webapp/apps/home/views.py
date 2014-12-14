# coding: utf-8

from django.shortcuts import render


def index(request):
    context = {
        'title': 'Home'
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'home/content.html', context)

    return render(request, 'home/index.html', context)
