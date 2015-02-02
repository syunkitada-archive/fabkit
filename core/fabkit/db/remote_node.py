# coding: utf-8

import yaml
from fabkit import env, conf, filer, sudo


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
