# coding: utf-8

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework import renderers

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from web_apps.api.models import File
from web_apps.api.serializers import UserSerializer, GroupSerializer, FileSerializer


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def perform_create(self, serializer):
        result = serializer.save(name=self.request.data.get('name'))
        print result


class FileRenderer(renderers.BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class FileViewSet(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = File.objects.all()
    serializer_class = FileSerializer
    renderer_classes = (FileRenderer, )
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        print self.request.data
        serializer.save(owner=self.request.user,
                        datafile=self.request.data.get('datafile'))

    def retrieve(self, request, pk=None):
        fileupload = get_object_or_404(self.queryset, pk=pk)
        datafile = open(fileupload.datafile.path, "rb").read()
        return Response(datafile)
