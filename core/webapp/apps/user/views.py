# coding: utf-8

from django.shortcuts import render, redirect
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.decorators import login_required


def index(request):
    users = serializers.serialize('json', User.objects.all().order_by('username'))
    context = {
        'title': 'User',
        'users': users,
    }
    if request.user.is_superuser:
        form = UserCreationForm(request.user)
        context['user_creation_form'] = form

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
            print form.errors
            return redirect('home:index')
    else:
        context = {
            'title': 'Change Password',
        }
        return render(request, 'user/change_password.html', context)


def create_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password1']
            user = User.objects.create_user(username, '', password)
            user.save()
            print 'create OK'
            redirect('user:create_user')

        else:
            print form.errors

        return redirect('user:index')
