# coding: utf-8

import pickle
import yaml
import os
import json
from web_lib import util
from web_apps.chat.utils import get_comments, get_cluster
from markdown import markdown
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
    agents = []
    if len(agent_clusters) == 0:
        pass
    else:
        if cluster_name is None:
            cluster_name = agent_clusters[0]

        cluster_dburl = database_map.get(cluster_name)
        cluster_dbapi = dbapi.DBAPI(cluster_dburl)
        agents = cluster_dbapi.get_agents()

    node_cluster = {}
    central_agents = []
    fabscript_map = {}
    node_map = {}
    for agent in agents:
        agent_fabscript_map = {}
        if agent.agent_type == 'central':
            central_agents.append(agent)

        elif agent.agent_type == 'agent':
            tmp_fabscript_map = json.loads(agent.fabscript_map)
            for cluster in tmp_fabscript_map.values():
                for fabscript_name, result in cluster['fabscript_map'].items():
                    agent_fabscript_map[fabscript_name] = result
                    fabscript = fabscript_map.get(fabscript_name, {
                        'status': 0,
                        'task_status': 0,
                    })

                    fabscript['status'] += result['status']
                    fabscript['task_status'] += result['task_status']
                    fabscript_map[fabscript_name] = fabscript

            node_map[agent.host] = {
                'status': agent.status,
                'check_timestamp': str(agent.check_timestamp),
                'setup_timestamp': str(agent.setup_timestamp),
                'fabscript_map': agent_fabscript_map,
            }

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

    context = {
        'title': 'Agent: ' + cluster_name,
        'cluster': cluster_name,
        'agents': agents,
        'central_agents': central_agents,
        'node_cluster': node_cluster,
        'agent_clusters': agent_clusters,
        'comments': get_comments(get_cluster(cluster)),
    }

    print agent_clusters

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'agent/content.html', context)

    return render(request, 'agent/index.html', context)
