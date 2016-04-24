# coding: utf-8

import pickle
import yaml
import os
import json
from web_apps.chat.utils import get_comments
from markdown import markdown
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from oslo_config import cfg
from db import dbapi

CONF = cfg.CONF


@login_required
def index(request, cluster=None):

    # for cluster, value in CONF.cluster.database_map.
    database_map = CONF.cluster.database_map

    agent_clusters = database_map.keys()
    agents = []
    if len(agent_clusters) == 0:
        pass
    else:
        if cluster is None:
            cluster = agent_clusters[0]

        cluster_dburl = database_map.get(cluster)
        cluster_dbapi = dbapi.DBAPI(cluster_dburl)
        agents = cluster_dbapi.get_agents()

    agent_clusters = json.dumps(agent_clusters)

    context = {
        'title': 'Agent',
        'cluster': cluster,
        'agents': agents,
        'agent_clusters': agent_clusters,
    }

    print agent_clusters

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'agent/content.html', context)

    return render(request, 'agent/index.html', context)
