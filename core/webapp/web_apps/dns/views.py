# coding: utf-8

import json
from web_apps.chat.utils import get_comments, get_cluster
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from oslo_config import cfg
from pdns import pdnsapi

CONF = cfg.CONF


@login_required
def index(request, cluster_name=None):
    pdns = pdnsapi.PdnsAPI()
    domains = pdns.get_domains()

    if len(domains) == 0:
        pass
    else:
        if cluster_name is None:
            domain = domains[0]
            cluster_name = domains[0].name
        else:
            for d in domains:
                if d.name == cluster_name:
                    domain = d
                    break
            else:
                domain = domains[0]
                cluster_name = domains[0].name

        records = pdns.get_records(domain_id=domain.id)

    if cluster_name is None:
        comments = []
    else:
        comments = get_comments(get_cluster(cluster_name))

    json_domains = []
    json_records = []
    for domain in domains:
        json_domains.append(domain.name)

    for record in records:
        data = {
            'name': record.name,
            'type': record.type,
            'content': record.content,
            'ttl': record.ttl,
        }
        json_records.append(data)

    if request.GET.get('query') == 'get_records':
        data = {
            'records': json_records,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")

    context = {
        'title': 'Domain: {0}'.format(cluster_name),
        'cluster': cluster_name,
        'records': json.dumps(json_records),
        'domains': json.dumps(json_domains),
        'comments': comments,
    }

    if request.META.get('HTTP_X_PJAX'):
        return render(request, 'dns/content.html', context)

    return render(request, 'dns/index.html', context)
