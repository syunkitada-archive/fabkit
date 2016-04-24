# coding: utf-8

import central
from db import dbapi
from oslo_config import cfg

CONF = cfg.CONF


def manage(*args, **kwargs):
    if 'help' in args:
        print 'help'

    elif 'setup' in args:
        centralapi = central.CentralAPI()
        result = centralapi.setup()
        print result

    elif 'cluster-list' in args:
        for cluster in CONF.cluster.database_map.keys():
            print cluster

    elif 'agent-list' in args:
        cluster = kwargs.get('cluster')

        def agent_list(cluster, dburl):
            print cluster
            clusterapi = dbapi.DBAPI(dburl)
            for agent in clusterapi.get_agents():
                print '{0}: {1}'.format(
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
