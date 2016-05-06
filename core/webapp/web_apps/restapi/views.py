# coding: utf-8

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import views
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .serializer import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FileUploadView(views.APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        print file_obj
        # ...
        # do some stuff with uploaded file
        # ...
        with open('/tmp/test', 'wb+') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        return Response(status=204)


# アップロードファイルを処理する関数を import します
from web_apps.restapi.forms import UploadFileForm


def handle_uploaded_file(f):
    destination = open('/tmp/file.txt', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        handle_uploaded_file(request.FILES['file'])

    return HttpResponse('debug')


from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet
from web_apps.restapi.models import FileUpload
from web_apps.restapi.serializer import FileUploadSerializer
from rest_framework import renderers


class JPEGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class FileUploadViewSet(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer
    renderer_classes = (JPEGRenderer, )
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        print self.request.data
        serializer.save(owner=self.request.user,
                        datafile=self.request.data.get('datafile'))

    def retrieve(self, request, pk=None):
        fileupload = get_object_or_404(self.queryset, pk=pk)
        datafile = open(fileupload.datafile.path, "rb").read()
        return Response(datafile)
