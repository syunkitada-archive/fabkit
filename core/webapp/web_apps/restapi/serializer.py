# coding: utf-8

from rest_framework import serializers

from django.contrib.auth.models import User
from web_apps.restapi.models import FileUpload


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class FileUploadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FileUpload
        fields = ('created', 'datafile')
        read_only_fields = ('created', 'datafile', 'owner')
