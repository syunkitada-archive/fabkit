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

    context = {
        'title': 'Agent',
        'cluster': cluster,
        'agent_cluster': {},
        'agent_clusters': [],
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'agent/content.html', context)

    return render(request, 'agent/index.html', context)
