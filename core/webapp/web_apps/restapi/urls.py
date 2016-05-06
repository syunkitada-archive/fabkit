# coding: utf-8

from django.conf.urls import include, url
from rest_framework import routers
from web_apps.restapi import views
from rest_framework.authtoken import views as authtoken_views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'files', views.FileUploadViewSet)

urlpatterns = [
    url(r'^token-auth/$', authtoken_views.obtain_auth_token, name='index'),
    # url(r'^upload_file/$', views.upload_file, name='file'),
    url(r'^', include(router.urls)),
]
