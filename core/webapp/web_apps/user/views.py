# coding: utf-8

import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from web_apps.chat.models import UserCluster
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt


@login_required
def index(request):
    users = serializers.serialize('json', User.objects.all().order_by('username'))
    context = {
        'title': 'User',
        'users': users,
    }
    if request.user.is_superuser:
        context['user_creation_form'] = UserCreationForm(request.user)

    context['password_change_form'] = PasswordChangeForm(user=request.user)

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'user/content.html', context)

    return render(request, 'user/index.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                next = request.GET.get('next', '/')
                return redirect(next)
            else:
                return redirect('user:login')
        else:
            return redirect('user:login')
    else:
        form = AuthenticationForm()
        context = {
            'title': 'Login',
            'form': form,
            'next': request.GET.get('next'),
        }

        return render(request, 'user/login.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('user:login')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            u = request.user
            password = request.POST['new_password1']
            u.set_password(password)
            u.save()
            return redirect('home:index')
        else:
            return redirect('home:index')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password1']
            user = User.objects.create_user(username, '', password)
            user.save()
            redirect('user:create')

        return redirect('user:index')


@csrf_exempt
def node_login(request):
    # Get User from sessionid
    session = Session.objects.get(session_key=request.POST.get('sessionid'))
    user_id = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(id=user_id)
    user_clusters = UserCluster.objects.all().filter(user=user).select_related()
    tmp_user_clusters = []
    for user_cluster in user_clusters:
        tmp_user_clusters.append({
            'cluster_name': user_cluster.cluster.cluster_name,
            'unread_comments_length': user_cluster.unread_comments_length,
        })

    data = json.dumps({
        'user': user.username,
        'user_clusters': tmp_user_clusters,
    })

    return HttpResponse(data)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def remove(request):
    if request.method == 'POST':
        targets = request.POST.getlist('target')
        for target in targets:
            user = User.objects.get(pk=target)
            user.delete()

        result = {
            'status': True,
        }

    else:
        result = {
            'status': True,
        }

    return HttpResponse(json.dumps(result))
