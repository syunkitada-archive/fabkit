# coding: utf-8

import json
from web_apps.chat.utils import get_comments, get_cluster
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from oslo_config import cfg
from db import dbapi

CONF = cfg.CONF


@login_required
def index(request, cluster_name=None):

    # for cluster, value in CONF.cluster.database_map.
    database_map = CONF.cluster.database_map

    agent_clusters = database_map.keys()
    tasks = []
    if len(agent_clusters) == 0:
        pass
    else:
        if cluster_name is None:
            cluster_name = agent_clusters[0]

        cluster_dburl = database_map.get(cluster_name)
        cluster_dbapi = dbapi.DBAPI(cluster_dburl)
        tasks = cluster_dbapi.get_all_tasks()

    agent_clusters = json.dumps(agent_clusters)

    if cluster_name is None:
        comments = []
    else:
        comments = get_comments(get_cluster(cluster_name))

    json_tasks = []
    for task in tasks:
        data = {
            'owner': task.owner,
            'method': task.method,
            'status': task.status,
            'target': task.target,
            'json_arg': task.json_arg,
            'msg': task.msg,
            'updated_at': str(task.updated_at),
            'created_at': str(task.created_at),
        }

        json_tasks.append(data)

    if request.GET.get('query') == 'get_tasks':
        data = {
            'tasks': json_tasks,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")

    tasks = json.dumps(json_tasks)

    context = {
        'title': 'Agent: {0}'.format(cluster_name),
        'cluster': cluster_name,
        'tasks': tasks,
        'agent_clusters': agent_clusters,
        'comments': comments,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'task/content.html', context)

    return render(request, 'task/index.html', context)
