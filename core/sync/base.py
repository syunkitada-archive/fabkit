# coding: utf-8

from fabkit import conf, sudo, scp, api, status
import datetime
from apps.sync.models import SyncState
from apps.node.models import Node, NodeCluster
from apps.fabscript.models import Fabscript
from django.core import serializers
import os
import time
import json


sync_state = None


@api.task
@api.hosts(conf.REMOTE_NODE)
def sync(task=None, option=None):
    global sync_state

    dump_dir = os.path.join(conf.STORAGE_DIR, 'dump/')
    node_file = os.path.join(dump_dir, 'node.json')
    fabscript_file = os.path.join(dump_dir, 'fabscript.json')
    node_cluster_file = os.path.join(dump_dir, 'node_cluster.json')
    timestamp = datetime.datetime.now()

    try:
        sync_state = SyncState.objects.get(pk=1)
    except SyncState.DoesNotExist:
        sync_state = SyncState(pk=1)
        sync_state.save()

    if task == 'dump':
        dump(timestamp=option)
    elif task == 'merge':
        merge()
    elif task == 'push':
        dump()
        scp(node_file, '/opt/fabkit/storage/dump/node.json')
        scp(node_cluster_file, '/opt/fabkit/storage/dump/node_cluster.json')
        scp(fabscript_file, '/opt/fabkit/storage/dump/fabscript.json')

        push_log = sudo('fab -f /opt/fabkit/fabfile sync:merge')
        sync_state.push_log = push_log
        sync_state.push_at = timestamp
        sync_state.save()

    elif task == 'pull':
        pull_at = time.mktime(sync_state.pull_at.timetuple())
        sudo('fab -f /opt/fabkit/fabfile sync:dump,{0}'.format(pull_at))
        scp('/opt/fabkit/storage/dump/node.json', node_file, is_receive=True)
        scp('/opt/fabkit/storage/dump/node_cluster.json', node_cluster_file, is_receive=True)
        scp('/opt/fabkit/storage/dump/fabscript.json', fabscript_file, is_receive=True)
        pull_log = merge()

        sync_state.pull_log = pull_log
        sync_state.pull_at = timestamp
        sync_state.save()

    return


def dump(timestamp=None):
    if timestamp:
        timestamp = datetime.datetime.fromtimestamp(float(datetime))
    else:
        timestamp = sync_state.push_at

    node = serializers.serialize('json', Node.objects.filter(updated_at__gt=timestamp))
    node_cluster = serializers.serialize('json',
                                         NodeCluster.objects.filter(updated_at__gt=timestamp))
    fabscript = serializers.serialize('json', Fabscript.objects.filter(updated_at__gt=timestamp))

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

    return 'dumped'


def merge(dump_dir=None):
    if not dump_dir:
        dump_dir = os.path.join(conf.STORAGE_DIR, 'dump/')
        if not os.path.exists(dump_dir):
            os.makedirs(dump_dir)

    node_filepath = os.path.join(dump_dir, 'node.json')
    node_cluster_filepath = os.path.join(dump_dir, 'node_cluster.json')
    fabscript_filepath = os.path.join(dump_dir, 'fabscript.json')
    msgs = []

    with open(node_filepath, 'r') as f:
        for deserialize_obj in serializers.deserialize("json", f.read()):
            tmp_obj = deserialize_obj.object
            try:
                obj = Node.objects.get(pk=tmp_obj.pk)
                if obj.updated_at >= tmp_obj.updated_at:
                    msgs.append([status.SYNC_REJECTED,
                                'rejected update node: {0}'.format(obj.path)])
                else:
                    tmp_obj.save()
                    msgs.append([status.SYNC_UPDATED,
                                'updated node: {0}'.format(obj.path)])

            except Node.DoesNotExist:
                tmp_obj.save()
                msgs.append([status.SYNC_CREATED,
                            'created node: {0}'.format(tmp_obj.path)])

    with open(node_cluster_filepath, 'r') as f:
        for deserialize_obj in serializers.deserialize("json", f.read()):
            tmp_obj = deserialize_obj.object
            try:
                obj = NodeCluster.objects.get(pk=tmp_obj.pk)
                if obj.updated_at >= tmp_obj.updated_at:
                    msgs.append([status.SYNC_REJECTED,
                                'rejected update node_cluster: {0}'.format(obj.name)])
                else:
                    tmp_obj.save()
                    msgs.append([status.SYNC_UPDATED,
                                'updated node_cluster: {0}'.format(obj.name)])

            except NodeCluster.DoesNotExist:
                tmp_obj.save()
                msgs.append([status.SYNC_CREATED,
                            'created node_cluster: {0}'.format(tmp_obj.name)])

    with open(fabscript_filepath, 'r') as f:
        for deserialize_obj in serializers.deserialize("json", f.read()):
            tmp_obj = deserialize_obj.object
            try:
                obj = Fabscript.objects.get(pk=tmp_obj.pk)
                if obj.updated_at >= tmp_obj.updated_at:
                    msgs.append([status.SYNC_REJECTED,
                                'rejected update fabscript: {0}'.format(obj.name)])
                else:
                    tmp_obj.save()
                    msgs.append([status.SYNC_UPDATED,
                                'updated fabscript: {0}'.format(obj.name)])

            except Fabscript.DoesNotExist:
                tmp_obj.save()
                msgs.append([status.SYNC_CREATED,
                            'created fabscript: {0}'.format(tmp_obj.name)])

    msgs_txt = json.dumps(msgs)
    print msgs_txt
    return msgs_txt
