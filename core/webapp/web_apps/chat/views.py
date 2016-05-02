# coding: utf-8

from django.contrib.auth.models import User
from web_apps.chat.models import Comment, UserCluster
from web_apps.chat.utils import get_comments, get_cluster
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

import json


@login_required
def index(request, cluster_name='all'):
    cluster = get_cluster(cluster_name)
    comments = get_comments(cluster)

    try:
        UserCluster.objects.get(user=request.user, cluster=cluster)
    except ObjectDoesNotExist:
        UserCluster.objects.create(user=request.user, cluster=cluster, unread_comments_length=0)

    context = {
        'title': 'Chat: ' + cluster_name,
        'comments': comments,
        'cluster': cluster_name,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'chat/content.html', context)

    return render(request, 'chat/index.html', context)


@csrf_exempt
def node_api(request, action):
    try:
        # Get User from sessionid
        session = Session.objects.get(session_key=request.POST.get('sessionid'))
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)

        if action == 'leave_from_cluster':
            cluster = request.POST.get('cluster')
            cluster = get_cluster(cluster)
            try:
                user_cluster = UserCluster.objects.get(
                    user=user, cluster=cluster)
                user_cluster.delete()
            except ObjectDoesNotExist:
                pass

            data = json.dumps({})
            return HttpResponse(data)

        elif action == 'post_comment':
            message = json.loads(request.POST.get('message'))
            cluster = message.get('cluster')
            text = message.get('text')
            cluster = get_cluster(cluster)

            user_clusters = UserCluster.objects.all().filter(cluster=cluster)
            for user_cluster in user_clusters:
                user_cluster.unread_comments_length += 1
                user_cluster.save()

            if cluster == "None" or cluster is None:
                comment = Comment.objects.create(user=user, text=text)
            else:
                comment = Comment.objects.create(user=user, cluster=cluster, text=text)

            data = json.dumps({
                'user': user.username,
                'text': text,
                'created_at': str(comment.created_at),
                'updated_at': str(comment.created_at),
            })

            return HttpResponse(data)

    except Exception, e:
        return HttpResponseServerError(str(e))
