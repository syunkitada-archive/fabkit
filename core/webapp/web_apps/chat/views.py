from django.contrib.auth.models import User
from web_apps.chat.models import Comments
from web_apps.chat.utils import get_comments

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required

import json


@login_required
def index(request, cluster='all'):
    comments = get_comments(cluster)

    context = {
        'title': 'Chat: ' + cluster,
        'comments': comments,
        'cluster': cluster,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'chat/content.html', context)

    return render(request, 'chat/index.html', context)


@csrf_exempt
def node_api(request):
    try:
        # Get User from sessionid
        session = Session.objects.get(session_key=request.POST.get('sessionid'))
        user_id = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(id=user_id)
        print 'DEBUG'

        data = json.loads(request.POST.get('data'))
        cluster = data.get('cluster')
        text = data.get('text')

        if cluster == "None" or cluster is None:
            comment = Comments.objects.create(user=user, text=text)
        else:
            comment = Comments.objects.create(user=user, cluster=cluster, text=text)

        data = json.dumps({
            'user': user.username,
            'text': text,
            'created_at': str(comment.created_at),
            'updated_at': str(comment.created_at),
        })

        return HttpResponse(data)

    except Exception, e:
        return HttpResponseServerError(str(e))
