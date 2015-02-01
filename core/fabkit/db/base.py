# coding: utf-8

import inspect
import yaml
import json
from fabkit import env, databag, status
from apps.fabscript.models import Fabscript
from node_model import update_cluster, update_node


def init_update_all():
    """
    Save env.node_map, env.cluster_map, env.fabscript_map to dababase.
    This is called before setup tasks.
    """

    cluster_map = {}
    for cluster, data in env.cluster_map.items():
        cluster_map[cluster] = update_cluster(cluster, data)
        env.cluster_map[cluster] = yaml.load(databag.decode_str(yaml.dump(data)))

    for host, data in env.node_map.items():
        cluster = cluster_map[data['path'].split('/', 1)[0]]
        update_node(status.REGISTERED, status.REGISTERED_MSG.format(data['path']),
                    host=host, cluster=cluster)

    for fabscript, data in env.fabscript_map.items():
        update_fabscript(fabscript, data)
        env.fabscript_map[cluster] = yaml.load(databag.decode_str(yaml.dump(data)))


def update_fabscript(name, data):
    try:
        fabscript = Fabscript.objects.get(name=name)
    except Fabscript.DoesNotExist:
        fabscript = Fabscript(name=name)

    fabscript.data = json.dumps(data)
    fabscript.save()

    return fabscript


# TODO 以下の関数は整理する必要がある

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
