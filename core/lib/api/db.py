# coding: utf-8

from fabric.api import env
import inspect
from lib import log
import yaml
import status_code
from webapp.node.models import Node, Fabscript, Result


def update_node(data, host=None):
    if not host:
        host = env.host

    try:
        node = Node.objects.get(host=host)
    except Node.DoesNotExist:
        node = Node(host=host)

    node.path = data.get('path', u'').decode('utf-8')
    node.ip = data.get('ip', u'').decode('utf-8')
    node.ssh = data.get('ssh', u'').decode('utf-8')
    node.uptime = data.get('uptime', u'').decode('utf-8')
    node.save()


def update_data_map(data, script_name=None):
    if not script_name:
        script_name = __get_script_name()

    try:
        fabscript = Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=script_name)
    data_str = yaml.dump(data)
    fabscript.data_map = data_str
    fabscript.save()


def update_connection_map(data, script_name=None):
    if not script_name:
        script_name = __get_script_name()

    try:
        fabscript = Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=script_name)

    data_str = yaml.dump(data)
    fabscript.connection_map = data_str
    fabscript.save()


def get(fabscript, key):
    pass


def get_connection(script_name, key):
    fabscript = Fabscript.objects.get(name=script_name)
    data = yaml.load(fabscript.connection_map)
    return data[key]


def setuped(status, msg, host=None, script_name=None):
    if not host:
        host = env.host

    if not script_name:
        script_name = __get_script_name()

    try:
        node = Node.objects.get(host=host)
    except Node.DoesNotExist:
        node = Node(host=host)
        node.save()

    try:
        fabscript = Fabscript.objects.get(name=script_name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=script_name)
        fabscript.save()

    try:
        result = Result.objects.get(node=node, fabscript=fabscript)
    except Result.DoesNotExist:
        result = Result(node=node, fabscript=fabscript)

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


def __get_script_name():
    stack = inspect.stack()[1:-11]
    for frame in stack:
        file = frame[1]
        if file.find('/fabscript/') > -1:
            return file.split('fabscript/', 1)[1].replace('.py', '').replace('/', '.')
