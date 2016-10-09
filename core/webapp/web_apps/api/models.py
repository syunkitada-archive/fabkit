# coding: utf-8

import datetime
from django.db import models
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from oslo_config import cfg

CONF = cfg.CONF


def upload_to(instance, filename):
    return 'group_{0}/{1}_{2}'.format(
        instance.group.id, filename,
        datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S'))


class File(models.Model):
    name = models.CharField(max_length=150)
    owner = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    generation = models.IntegerField(default=1)
    file = models.FileField(
        storage=FileSystemStorage(location=CONF._webapp_storage_dir),
        upload_to=upload_to)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
