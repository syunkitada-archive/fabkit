# coding: utf-8

import inspect
import yaml
import json
from fabkit import env, conf, filer, sudo, databag
from apps.node.models import Node, NodeCluster
from apps.fabscript.models import Fabscript
from django.db import transaction


def update_remote_node(data, host=None):
    '''
    リモート上にkey-valueのデータベースを持つ
    '''
    if not host:
        host = env.host

    remote_storage = conf.REMOTE_STORAGE
    filer.mkdir(remote_storage)
    target = '{0}node.yaml'.format(remote_storage)
    filer.template(target, src_str=yaml.dump(data))


def get_remote_node():
    node_file = '/opt/chefric/storage/node.yaml'
    if filer.exists(node_file):
        return yaml.load(sudo('cat {0}'.format(node_file)))

    return {}


def get_recent_nodes(length=30):
    nodes = Node.objects.order_by('updated_at').all()[:length]
    return nodes


def get_error_nodes(length=30):
    nodes = Node.objects.filter(status__gt=0)[:length]
    return nodes


def get_node(env_node):
    path = env_node['path']
    try:
        node = Node.objects.get(path=path)
        node.data = env_node['data']
    except Node.DoesNotExist:
        node = Node(path=path)

        rsplited_path = path.rsplit('/', 1)
        if len(rsplited_path) > 1:
            cluster = rsplited_path[0]

            try:
                node_cluster = NodeCluster.objects.get(name=cluster)
                node_cluster.is_deleted = False
            except NodeCluster.DoesNotExist:
                node_cluster = NodeCluster(name=cluster)

            node_cluster.save()

        else:
            node_cluster = None

        node.cluster = node_cluster
        node.save()

    return node


def create_fabscript(script_name):
    try:
        fabscript = Fabscript.objects.get(name=script_name)
        if fabscript.is_deleted:
            fabscript.is_deleted = False
            fabscript.save()
    except Fabscript.DoesNotExist:
        # 並列実行時に、同時に新規作成しようとすると刺さるためトランザクション化
        create_new_fabscript(script_name)


@transaction.atomic
def create_new_fabscript(script_name):
    fabscript = Fabscript(name=script_name)
    fabscript.save()


def update_data(data, script_name=None):
    if not script_name:
        script_name = __get_script_name()

    try:
        fabscript = Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=script_name)

    data_str = json.dumps(data)
    fabscript.data = data_str
    fabscript.save()


def update_link(data, script_name=None):
    if not script_name:
        script_name = __get_script_name()

    try:
        fabscript = Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=script_name)

    data_str = json.dumps(data)
    fabscript.link = data_str
    fabscript.save()


def get_link(script_name, key):
    # 参照先のscript
    fabscript = Fabscript.objects.get(name=script_name)

    # 参照元のscript
    tmp_fabscript = __get_script_name()
    if tmp_fabscript:
        linked_fabscript = '{0}:{1}'.format(tmp_fabscript, key)
        linked_fabscripts = set(yaml.load(fabscript.linked_fabscripts))
        linked_fabscripts.add(linked_fabscript)
        fabscript.linked_fabscripts = json.dumps(list(linked_fabscripts))
        fabscript.save()

    link_str = databag.decode_str(fabscript.link)
    data = json.loads(link_str)
    return data[key]


def setuped(status, msg, is_init=False, host=None, fabscript=None):
    if not host:
        host = env.host

    if fabscript:
        from fabkit import util
        util.update_log(fabscript, status, msg)
        msg = '{0}: {1}'.format(fabscript, msg)

    env_node = env.node_map.get(host)
    node = get_node(env_node)

    if is_init:
        logs = json.loads(node.logs)
        logs_all = json.loads(node.logs_all)
        logs_all.extend(logs)
        logs_all = logs_all[-conf.WEB_LOG_LENGTH:]
        node.logs_all = json.dumps(logs_all)

    node.is_deleted = False
    node.logs = json.dumps(env_node['logs'])
    node.status = status
    node.msg = msg
    node.save()


def is_setuped(host, script_name, status=0):
    return True
    # TODO is_setuped
    # try:
    #     node = Node.objects.get(host=host)
    #     fabscript = Fabscript.objects.get(name=script_name)
    #     result = Result.objects.get(node=node, fabscript=fabscript)
    #     if result.status == status:
    #         return 0

    # except Node.DoesNotExist:
    #     msg = '{0} does not exist'.format(host)
    #     log.warning(msg)
    #     return status_code.NODE_DOES_NOT_EXIST, msg

    # except Fabscript.DoesNotExist:
    #     msg = '{0} does not exist'.format(script_name)
    #     log.warning(msg)
    #     return status_code.FABSCRIPT_DOES_NOT_EXIST, msg

    # except Result.DoesNotExist:
    #     msg = '{0} does not exist'.format(host, script_name)
    #     log.warning(msg)
    #     return status_code.RESULT_DOES_NOT_EXIST, msg

    # msg = '{0}:{1} is not setuped'. format(host, script_name)
    # log.warning(msg)
    # return status_code.IS_NOT_SETUPED, msg


def __get_script_name(is_reqursive=False):
    scripts = []
    stack = inspect.stack()[1:]
    for frame in stack:
        file = frame[1]
        if file.find('/fabscript/') > -1:
            script = file.split('fabscript/', 1)[1].replace('.py', '').replace('/', '.')
            if not is_reqursive:
                return script

            if 'setup' not in frame[0].f_code.co_names:
                continue

            scripts.insert(0, script)

    if len(scripts) == 0:
        return None

    return '>'.join(scripts)
