# coding: utf-8

from django.db import models
from apps.node.models import Node
from apps.fabscript.models import Fabscript


class Result(models.Model):
    node = models.ForeignKey(Node, null=True)
    fabscript = models.ForeignKey(Fabscript, null=True)
    status = models.IntegerField(default=0)
    msg = models.CharField(default=u'', max_length=1024)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '{0}:{1} [{2}]'.format(self.node, self.fabscript, self.status)
