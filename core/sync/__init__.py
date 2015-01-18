# coding: utf-8

from fabric.api import (task,
                        env,
                        hosts)
from lib import conf, util, log
from lib.api import sudo, db, filer, status_code, run, scp
import datetime
from apps.sync.models import Sync
from apps.node.models import Node, NodeCluster
from apps.fabscript.models import Fabscript
from django.core import serializers
import os


sync = None


@task
@hosts('dev01.vagrant.mydns.jp')
def sync(task=None, option=None):
    dump_dir = os.path.join(conf.STORAGE_DIR, 'dump/')
    node_file = os.path.join(dump_dir, 'node.json')
    fabscript_file = os.path.join(dump_dir, 'fabscript.json')
    timestamp = datetime.now()

    try:
        sync = Sync.objects.get(pk=1)
    except Sync.DoesNotExist:
        sync = Sync(pk=1)
        sync.save()

    if task == 'dump':
        dump()
    elif task == 'merge':
        merge()
    elif task == 'push':
        dump()
        scp(node_file, '/opt/fabkit/storage/dump/node.json')
        scp(node_file, '/opt/fabkit/storage/dump/node.json')
        scp(fabscript_file, '/opt/fabkit/storage/dump/fabscript.json')

        push_log = sudo('fab -f /opt/fabkit/fabfile sync:merge')
        sync.push_log = push_log
        sync.push_at = timestamp
        sync.save()

    elif task == 'pull':
        sudo('fab -f /opt/fabkit/fabfile sync:dump')
        scp('/opt/fabkit/storage/dump/node.json', node_file, is_receive=True)
        scp('/opt/fabkit/storage/dump/fabscript.json', fabscript_file, is_receive=True)
        pull_log = merge()

        sync.pull_at = timestamp
        sync.pull_log = pull_log
        sync.save()

    return


def dump(dump_dir=None, timestamp=None):

    if not timestamp:
        timestamp = sync.push_at

    node = serializers.serialize('json', Node.objects.filter(updated_at__gt=timestamp))
    node_cluster = serializers.serialize('json',
                                         NodeCluster.objects.filter(updated_at__gt=timestamp))
    fabscript = serializers.serialize('json', Fabscript.objects.filter(updated_at__gt=timestamp))

    if not dump_dir:
        dump_dir = os.path.join(conf.STORAGE_DIR, 'dump/')
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)

    node_filepath = os.path.join(dump_dir, 'node.json')
    node_cluster_filepath = os.path.join(dump_dir, 'node_cluster.json')
    fabscript_filepath = os.path.join(dump_dir, 'fabscript.json')

    with open(node_filepath, 'w') as f:
        f.write(node)

    with open(node_cluster_filepath, 'w') as f:
        f.write(node_cluster)

    with open(fabscript_filepath, 'w') as f:
        f.write(fabscript)


def merge(dump_dir=None):
    if not dump_dir:
        dump_dir = os.path.join(conf.STORAGE_DIR, 'dump/')
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)

    node_filepath = os.path.join(dump_dir, 'node.json')
    node_cluster_filepath = os.path.join(dump_dir, 'fabscript.json')
    fabscript_filepath = os.path.join(dump_dir, 'fabscript.json')

    with open(node_filepath, 'r') as f:
        for deserialize_obj in serializers.deserialize("json", f.read()):
            tmp_obj = deserialize_obj.object
            try:
                obj = Node.objects.get(pk=tmp_obj.pk)
                if obj.updated_at < tmp_obj.updated_at:
                    tmp_obj.save()
            except Node.DoesNotExist:
                tmp_obj.save()

    with open(node_cluster_filepath, 'r') as f:
        for deserialize_obj in serializers.deserialize("json", f.read()):
            tmp_obj = deserialize_obj.object
            try:
                obj = NodeCluster.objects.get(pk=tmp_obj.pk)
                if obj.updated_at < tmp_obj.updated_at:
                    tmp_obj.save()
            except Node.DoesNotExist:
                tmp_obj.save()

    with open(fabscript_filepath, 'r') as f:
        for deserialize_obj in serializers.deserialize("json", f.read()):
            tmp_obj = deserialize_obj.object
            try:
                obj = Fabscript.objects.get(pk=tmp_obj.pk)
                if obj.updated_at < tmp_obj.updated_at:
                    tmp_obj.save()
            except Fabscript.DoesNotExist:
                tmp_obj.save()
