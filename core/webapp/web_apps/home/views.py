# coding: utf-8

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return redirect(reverse('node:index'))
