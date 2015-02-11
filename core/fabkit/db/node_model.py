# noqa
from apps.node.models import Node, NodeCluster
import json
from fabkit import status, conf


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


def update_node(status_code, msg, path, cluster, data, is_init=False):
    try:
        node = Node.objects.get(path=path)
    except Node.DoesNotExist:
        node = Node(path=path)
        node.cluster = cluster

    if status_code == status.REGISTERED:
        logs = json.loads(node.logs)
        logs_all = json.loads(node.logs_all)
        logs_all.append(logs)
        logs_all = logs_all[-conf.WEB_LOG_LENGTH:]
        node.logs_all = json.dumps(logs_all)

    node.is_deleted = False
    node.logs = json.dumps(data['fabscript_map'])
    node.status = status_code
    node.msg = msg
    node.save()

    return node


def get_recent_nodes(length=30):
    nodes = Node.objects.order_by('updated_at').all()[:length]
    return nodes


def get_error_nodes(length=30):
    nodes = Node.objects.filter(status__gt=0)[:length]
    return nodes
