# coding: utf-8

from fabric.api import env
from lib import conf
import os
from webapp.node.models import Node, Fabscript


def update_node(host, node):
    try:
        node = Node.objects.get(host=host)
    except Node.DoesNotExist:
        node = Node(host=host, ip=node.get('ip', ''), uptime=node.get('uptime', ''))

    node.save()


def update_fabscript(fabscript_name, data):
    pass


def update_connection(fabscript, data):
    pass


def get(fabscript, key):
    pass


def get_connection(fabscript, key):
    pass


def setuped(key, status, host=None):
    pass


def wait_setuped(host, key):
    pass
