# coding: utf-8

from django.db import models
import datetime


class Sync(models.Model):
    log = models.CharField(default=u'', max_length=255, unique=True)
    pull_at = models.DateTimeField(auto_now=False, default=datetime.datetime(2000, 1, 1))
    push_at = models.DateTimeField(auto_now=False, default=datetime.datetime(2000, 1, 1))
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.path
