# coding: utf-8

from django.conf.urls import include, url
from rest_framework import routers
from web_apps.api import views
from rest_framework.authtoken import views as authtoken_views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'files', views.FileViewSet)

urlpatterns = [
    url(r'^authtoken/$', authtoken_views.obtain_auth_token, name='index'),
    url(r'^', include(router.urls)),
]
