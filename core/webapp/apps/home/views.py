# coding: utf-8

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    context = {
        'title': 'Home',
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'home/content.html', context)

    return render(request, 'home/index.html', context)
