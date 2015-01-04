# coding: utf-8

from django.db import models
from apps.node.models import Node, NodeCluster


class Result(models.Model):
    """
    logs = [  # 最後の実行時logのみ
        {
            'fabscript': '',
            'status': '',
            'msg': '',
        }
    ]

    TODO logs_allを100件までしか保存できないようにする
    実行開始時にlogsをlogs_allに移す
    logs_all = [  # すべてのlog(100件)

    ]
    """
    node = models.ForeignKey(Node, null=True, unique=True)
    cluster = models.ForeignKey(NodeCluster, null=True)
    node_path = models.CharField(default=u'', max_length=255)
    status = models.IntegerField(default=0)
    msg = models.CharField(default=u'', max_length=1024)
    logs = models.CharField(default=u'[]', max_length=1024)
    logs_all = models.CharField(default=u'[]', max_length=1024)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '{0}:{1} [{2}]'.format(self.node, self.msg, self.status)


class ChefResult(models.Model):
    node = models.CharField(default=u'', max_length=255, unique=True)
    status = models.IntegerField(default=0)
    msg = models.CharField(default=u'', max_length=1024)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return '{0}:{1} [{2}]'.format(self.node, self.msg, self.status)
