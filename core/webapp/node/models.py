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


class Fabscript(models.Model):
    name = models.CharField(default=u'', max_length=255, unique=True)
    data_map = models.CharField(default=u'', max_length=1024)
    connection_map = models.CharField(default=u'', max_length=1024)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.name


class Result(models.Model):
    node = models.ForeignKey(Node, null=True)
    fabscript = models.ForeignKey(Fabscript, null=True)
    status = models.IntegerField(default=0)
    msg = models.CharField(default=u'', max_length=1024)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '{0}:{1} [{2}]'.format(self.node, self.fabscript, self.status)
