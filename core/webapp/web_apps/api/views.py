# coding: utf-8

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from rest_framework import renderers

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist

from web_apps.api.models import File
from web_apps.api.serializers import UserSerializer, GroupSerializer, FileSerializer


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, pk=None):
        group_name = request.POST['group']
        user = User.objects.get(username=pk)
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        user.save()
        return Response(status=status.HTTP_200_OK)


class GroupViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def perform_create(self, serializer):
        result = serializer.save(name=self.request.data.get('name'))


class FileRenderer(renderers.BaseRenderer):
    media_type = 'application/x-tar'
    format = '.multipart'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class FileViewSet(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = File.objects.all()
    serializer_class = FileSerializer
    renderer_classes = (FileRenderer,)
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        group_name = self.request.POST['group']
        name = self.request.POST['name']
        group = Group.objects.get(name=group_name)
        files = File.objects.all().filter(name=name, group=group)
        for file in files:
            file.generation += 1
            if file.generation > 2:
                file.file.delete()
                file.delete()
            else:
                file.save()

        serializer.save(owner=self.request.user,
                        group=group,
                        name=name,
                        file=self.request.data.get('datafile'))

    def retrieve(self, request, pk=None):
        group_name = pk
        group = Group.objects.get(name=group_name)
        filename = self.request.GET['name']
        generation = self.request.GET.get('generation', 1)
        try:
            file = File.objects.get(name=filename, group=group, generation=generation)
            datafile = open(file.file.path, "rb").read()
            return Response(datafile)

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
