# coding: utf-8

import json
from web_lib import util
from web_apps.chat.utils import get_comments, get_cluster
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from oslo_config import cfg
from db import dbapi

CONF = cfg.CONF


@login_required
def index(request, cluster_name=None):
    # for cluster, value in CONF.cluster.database_map.
    database_map = CONF.cluster.database_map

    agent_clusters = database_map.keys()
    if len(agent_clusters) == 0:
        pass
    else:
        if cluster_name is None:
            cluster_name = agent_clusters[0]

        cluster_dburl = database_map.get(cluster_name)
        cluster_dbapi = dbapi.DBAPI(cluster_dburl)
        events = cluster_dbapi.get_events()

    node_cluster = {}
    fabscript_map = {}
    node_map = {}

    util.update_fabscript_map(fabscript_map)

    node_cluster = {
        '__status': {
            'fabscript_map': fabscript_map,
            'node_map': node_map,
        },
        'datamap': {},
    }

    agent_clusters = json.dumps(agent_clusters)
    node_cluster = json.dumps(node_cluster)

    if cluster_name is None:
        comments = []
    else:
        comments = get_comments(get_cluster(cluster_name))

    context = {
        'title': 'Event: {0}'.format(cluster_name),
        'cluster': cluster_name,
        'events': events,
        'node_cluster': node_cluster,
        'agent_clusters': agent_clusters,
        'comments': comments,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'event/content.html', context)

    return render(request, 'event/index.html', context)
