# coding: utf-8

from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return redirect(reverse('node:index'))


def test(request):
    return render(request, 'node/test.html', {})
