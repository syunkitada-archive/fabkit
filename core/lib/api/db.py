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
from apps.node.models import Node
from apps.fabscript.models import Fabscript
from apps.result.models import Result, ChefResult


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


def update_node(host=None):
    if not host:
        host = env.host

    env_node = env.node_map[host]

    try:
        node = Node.objects.get(path=env_node['path'])
    except Node.DoesNotExist:
        node = Node(path=env_node['path'])

    node.host = host
    node.path = env_node.get('path', u'').decode('utf-8')
    node.ip = env_node.get('ip', u'').decode('utf-8')
    node.ssh = env_node.get('ssh', u'').decode('utf-8')
    node.uptime = env_node.get('uptime', u'').decode('utf-8')
    node.save()


def create_fabscript(script_name):
    try:
        fabscript = Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=script_name)

    fabscript.save()


def update_connection(data, script_name=None):
    if not script_name:
        script_name = __get_script_name()

    try:
        fabscript = Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=script_name)

    data_str = json.dumps(data)
    fabscript.connection = data_str
    fabscript.save()


def get_connection(script_name, key):
    fabscript = Fabscript.objects.get(name=script_name)

    connected_fabscript = '{0}:{1}'.format(__get_script_name(True), key)
    connected_fabscripts = set(yaml.load(fabscript.connected_fabscripts))
    connected_fabscripts.add(connected_fabscript)
    fabscript.connected_fabscripts = json.dumps(list(connected_fabscripts))
    fabscript.save()
    connection_str = databag.decode_str(fabscript.connection)
    data = json.loads(connection_str)
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
    try:
        node = Node.objects.get(path=env_node['path'])
    except Node.DoesNotExist:
        node = Node(path=env_node['path'])
        node.save()

    try:
        result = Result.objects.get(node=node)
    except Result.DoesNotExist:
        result = Result(node=node)

    if is_init:
        logs = json.loads(result.logs)
        logs_all = json.loads(result.logs_all)
        logs_all.extend(logs)
        result.logs_all = json.dumps(logs_all)

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
    stack = inspect.stack()[1:-11]
    for frame in stack:
        file = frame[1]
        if file.find('/fabscript/') > -1:
            script = file.split('fabscript/', 1)[1].replace('.py', '').replace('/', '.')
            if not is_reqursive:
                return script

            scripts.insert(0, script)

    return '>'.join(scripts)
