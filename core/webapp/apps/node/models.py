# coding: utf-8

from django.db import models


class NodeCluster(models.Model):
    name = models.CharField(default=u'', max_length=255, unique=True)
    data = models.CharField(default=u'{}', max_length=100000)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.path


class Node(models.Model):
    """
    logs = [  # 最後の実行時logのみ
        {
            'fabscript': '',
            'status': '',
            'msg': '',
        }
    ]

    実行開始時にlogsをlogs_allに移す
    logs_all = [  # すべてのlog(100件)

    ]
    """

    path = models.CharField(default=u'', max_length=255, unique=True)
    cluster = models.ForeignKey(NodeCluster, null=True)
    data = models.CharField(default=u'{}', max_length=10000)

    # ip = models.CharField(default=u'', max_length=255)
    # uptime = models.CharField(default=u'', max_length=255)
    # ssh = models.CharField(default=u'', max_length=255)

    status = models.IntegerField(default=0)
    msg = models.CharField(default=u'', max_length=1024)
    logs = models.CharField(default=u'[]', max_length=1024)
    logs_all = models.CharField(default=u'[]', max_length=1024)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.path
