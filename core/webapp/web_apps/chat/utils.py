# coding: utf-8

from web_apps.chat.models import Comment, Cluster
from django.core.exceptions import ObjectDoesNotExist


def get_cluster(cluster_name):
    try:
        cluster = Cluster.objects.get(cluster_name=cluster_name)
    except ObjectDoesNotExist:
        cluster = Cluster.objects.create(cluster_name=cluster_name)

    return cluster


def get_comments(cluster=None):
    if cluster is None:
        comments = Comment.objects.select_related().all().order_by('created_at').reverse()[:100]
    else:
        comments = Comment.objects.select_related().filter(cluster=cluster).order_by('created_at').reverse()[:100]  # noqa

    return comments
