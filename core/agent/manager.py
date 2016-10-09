# coding: utf-8

import central
from db import dbapi
from oslo_config import cfg

CONF = cfg.CONF


def manage(*args, **kwargs):
    if 'setup' in args:
        centralapi = central.CentralAPI()
        result = centralapi.setup()
        print result

    elif 'cluster-list' in args:
        for cluster in CONF.cluster.database_map.keys():
            print cluster

    elif 'agent-setup' in args:
        cluster = kwargs.get('cluster')
        dburl = CONF.cluster.database_map.get(cluster)
        clusterapi = dbapi.DBAPI(dburl)
        setup_tasks = clusterapi.get_request_tasks(method='setup')
        if len(setup_tasks) > 0:
            print 'Already exists setup_task'
            for task in setup_tasks:
                print '  * {0}({1}): {2}'.format(
                    task.method,
                    task.json_arg,
                    task.status,
                )
            return

        clusterapi.create_task({
            'method': 'setup',
        })

    elif 'agent-list' in args:
        cluster = kwargs.get('cluster')

        def agent_list(cluster, dburl):
            print cluster
            clusterapi = dbapi.DBAPI(dburl)
            for agent in clusterapi.get_agents():
                print '{0}: {1}: {2}'.format(
                    agent.agent_type,
                    agent.host,
                    agent.status,
                )

        if cluster is None:
            for cluster, dburl in CONF.cluster.database_map.items():
                agent_list(cluster, dburl)

        else:
            print cluster
            dburl = CONF.cluster.database_map.get(cluster)
            if dburl is not None:
                agent_list(cluster, dburl)
            else:
                print 'cluster: {0} is not found.'.format(cluster)
