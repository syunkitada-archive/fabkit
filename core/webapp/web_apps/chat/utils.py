# coding: utf-8

from web_apps.chat.models import Comments


def get_comments(cluster=None):
    if cluster is None:
        comments = Comments.objects.select_related().all().order_by('created_at').reverse()[:100]
    else:
        comments = Comments.objects.select_related().filter(cluster=cluster).order_by('created_at').reverse()[:100]  # noqa

    return comments
