# noqa
from apps.node.models import Node, NodeCluster
import json
from fabkit import env, conf


def update_cluster(name, data={}):
    try:
        cluster = NodeCluster.objects.get(name=name)
        if cluster.is_deleted:
            cluster.is_deleted = False
    except NodeCluster.DoesNotExist:
        cluster = NodeCluster(name=name)

    cluster.data = json.dumps(data)
    cluster.save()
    return cluster


def update_node(status, msg, is_init=False, host=None, cluster=None, fabscript=None):
    if not host:
        host = env.host

    if fabscript:
        from fabkit import util
        util.update_log(fabscript, status, msg)
        msg = '{0}: {1}'.format(fabscript, msg)

    env_node = env.node_map.get(host)
    path = env_node['path']

    try:
        node = Node.objects.get(path=path)
        node.data = env_node['data']
    except Node.DoesNotExist:
        node = Node(path=path)

    if is_init:
        logs = json.loads(node.logs)
        logs_all = json.loads(node.logs_all)
        logs_all.extend(logs)
        logs_all = logs_all[-conf.WEB_LOG_LENGTH:]
        node.logs_all = json.dumps(logs_all)

    if cluster:
        node.cluster = cluster

    node.is_deleted = False
    node.logs = json.dumps(env_node['logs'])
    node.status = status
    node.msg = msg
    node.save()

    return node


def get_recent_nodes(length=30):
    nodes = Node.objects.order_by('updated_at').all()[:length]
    return nodes


def get_error_nodes(length=30):
    nodes = Node.objects.filter(status__gt=0)[:length]
    return nodes
