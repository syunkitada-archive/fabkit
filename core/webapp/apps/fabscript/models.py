# coding: utf-8

from django.db import models


class Fabscript(models.Model):
    name = models.CharField(default=u'', max_length=255, unique=True)
    connection = models.CharField(default=u'{}', max_length=1024)
    connected_fabscripts = models.CharField(default=u'[]', max_length=1024)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.name
