# coding: utf-8

from django.shortcuts import render
from apps.fabscript.models import Fabscript


def index(request):
    fabscripts = Fabscript.objects.all()
    return render(request, 'fabscript/index.html', {'fabscripts': fabscripts})
