# coding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage


def upload_to(instance, filename):
    return '/tmp/{}/{}'.format(instance.user_id, filename)

fs = FileSystemStorage(location='/tmp/')


class FileUpload(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    datafile = models.FileField(storage=fs, upload_to='test.txt')
