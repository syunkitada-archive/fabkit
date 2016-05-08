# coding: utf-8

from django.db import models
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage


fs = FileSystemStorage(location='/tmp/')


def upload_to(instance, filename):
    return 'group_{0}/{1}'.format(instance.group.id, filename)


class File(models.Model):
    owner = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    file = models.FileField(storage=fs, upload_to=upload_to)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
