# coding: utf-8

from django.db import models


class Node(models.Model):
    host = models.CharField(default=u'', max_length=255, unique=True)
    ip = models.CharField(default=u'', max_length=255)
    path = models.CharField(default=u'', max_length=255)
    uptime = models.CharField(default=u'', max_length=255)
    ssh = models.CharField(default=u'', max_length=255)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.host
