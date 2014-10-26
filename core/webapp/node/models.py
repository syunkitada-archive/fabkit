# coding: utf-8

from django.db import models


class Node(models.Model):
    host = models.CharField(u'hostname', max_length=255, unique=True)
    ip = models.CharField(u'ip', max_length=255)
    uptime = models.CharField(u'uptime', max_length=255)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '{0}'.format(self.host)


class Fabscript(models.Model):
    node = models.ForeignKey(Node, verbose_name=u'node', related_name='fabrun')
    fabrun = models.CharField(u'fabrun', max_length=255)
    db = models.CharField(u'db', max_length=255)
    status = models.IntegerField(u'status')
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)
