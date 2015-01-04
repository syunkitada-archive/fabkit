# coding: utf-8

from fabric.api import env
import inspect
from lib import log, conf
import yaml
import json
import status_code
import filer
import databag
from api import sudo
from apps.node.models import Node, NodeCluster
from apps.fabscript.models import Fabscript
from apps.result.models import Result, ChefResult
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


def get_node(env_node):
    path = env_node['path']
    try:
        node = Node.objects.get(path=path)
    except Node.DoesNotExist:
        node = Node(path=path)

        rsplited_path = path.rsplit('/', 1)
        if len(rsplited_path) > 1:
            cluster = rsplited_path[0]

            try:
                node_cluster = NodeCluster.objects.get(name=cluster)
            except NodeCluster.DoesNotExist:
                node_cluster = NodeCluster(name=cluster)
                node_cluster.save()

        else:
            node_cluster = None

        node.cluster = node_cluster
        node.save()

    return node


def update_node(host=None):
    if not host:
        host = env.host

    env_node = env.node_map[host]

    node = get_node(env_node)

    node.host = host
    node.path = env_node.get('path', u'').decode('utf-8')
    node.ip = env_node.get('ip', u'').decode('utf-8')
    node.ssh = env_node.get('ssh', u'').decode('utf-8')
    node.uptime = env_node.get('uptime', u'').decode('utf-8')
    node.save()


def create_fabscript(script_name):
    try:
        Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        # 並列実行時に、同時に新規作成しようとすると刺さるためトランザクション化
        create_new_fabscript(script_name)


@transaction.commit_manually
def create_new_fabscript(script_name):
    try:
        fabscript = Fabscript(name=script_name)
        fabscript.save()
    except:
        transaction.rollback()
    else:
        transaction.commit()


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


def setuped_chef(status, msg, host=None, script_name=None):
    if not host:
        host = env.host

    try:
        result = ChefResult.objects.get(node=host)
    except Result.DoesNotExist:
        result = ChefResult(node=host)

    result.status = status
    result.msg = msg
    result.save()


def setuped(status, msg, is_init=False, host=None):
    if not host:
        host = env.host

    env_node = env.node_map.get(host)
    node = get_node(env_node)

    try:
        result = Result.objects.get(node=node)
    except Result.DoesNotExist:
        result = Result(node=node)

    if is_init:
        logs = json.loads(result.logs)
        logs_all = json.loads(result.logs_all)
        logs_all.extend(logs)
        result.logs_all = json.dumps(logs_all)

    result.cluster = node.cluster
    result.node_path = env_node['path']
    result.logs = json.dumps(env_node['logs'])
    result.status = status
    result.msg = msg
    result.save()


def is_setuped(host, script_name, status=0):
    try:
        node = Node.objects.get(host=host)
        fabscript = Fabscript.objects.get(name=script_name)
        result = Result.objects.get(node=node, fabscript=fabscript)
        if result.status == status:
            return 0

    except Node.DoesNotExist:
        msg = '{0} does not exist'.format(host)
        log.warning(msg)
        return status_code.NODE_DOES_NOT_EXIST, msg

    except Fabscript.DoesNotExist:
        msg = '{0} does not exist'.format(script_name)
        log.warning(msg)
        return status_code.FABSCRIPT_DOES_NOT_EXIST, msg

    except Result.DoesNotExist:
        msg = '{0} does not exist'.format(host, script_name)
        log.warning(msg)
        return status_code.RESULT_DOES_NOT_EXIST, msg

    msg = '{0}:{1} is not setuped'. format(host, script_name)
    log.warning(msg)
    return status_code.IS_NOT_SETUPED, msg


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
