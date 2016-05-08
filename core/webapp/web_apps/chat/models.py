# coding: utf-8

from django.db import models
from django.contrib.auth.models import User


class Cluster(models.Model):
    cluster_name = models.CharField(max_length=255)
    cluster_info = models.CharField(max_length=1000, default='')
    is_public = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User)
    cluster = models.ForeignKey(Cluster, related_name='cluster')
    text = models.CharField(max_length=550)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserCluster(models.Model):
    user = models.ForeignKey(User)
    cluster = models.ForeignKey(Cluster)
    unread_comments_length = models.IntegerField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
