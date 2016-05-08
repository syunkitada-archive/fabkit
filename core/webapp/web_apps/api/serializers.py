# coding: utf-8

from rest_framework import serializers

from django.contrib.auth.models import User, Group
from web_apps.api.models import File


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ('file', 'created_at', 'updated_at')
        read_only_fields = ('created', 'datafile', 'owner')
