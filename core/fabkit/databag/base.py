# coding: utf-8

import re
import os
import yaml
from fabkit import cmd
from oslo_config import cfg

CONF = cfg.CONF


def set(key_path, value):
    key, data_file = __get_key_file(key_path)
    data_dir = os.path.dirname(data_file)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    databag = get_databag(key_path)
    databag.update({key: value})

    with open(data_file, 'w') as f:
        yaml.dump(databag, f)

    return


def get(key_path):
    splited_key = key_path.rsplit('.', 1)
    databag = get_databag(key_path)
    return databag[splited_key[1]]


def exists(key_path):
    splited_key = key_path.rsplit('.', 1)
    databag = get_databag(key_path)
    return (splited_key[1] in databag)


def get_databag(key_path):
    key, data_file = __get_key_file(key_path)

    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = yaml.load(f)
    else:
        data = {}

    return data


def __get_key_file(key_path):
    splited_key = key_path.rsplit('.', 1)
    if len(splited_key) == 1:
        print 'key\'s format is [filepath].[keyname]'
        print 'e.g. common/database/mysql.password'
        return

    data_file = splited_key[0] + '.yaml'
    data_file = os.path.join(CONF._databag_dir, data_file)
    key = splited_key[1]
    return key, data_file


def print_list(key=None):
    if key:
        path = os.path.join(CONF._databag_dir, key)
    else:
        path = CONF._databag_dir

    output = cmd('find {0}'.format(path))
    RE_DATABAG_YAML = re.compile('{0}/(.*).yaml'.format(CONF._databag_dir))
    bags = RE_DATABAG_YAML.findall(output[1])
    if len(bags) == 0:
        print 'Databag was not found.'
    else:
        for bag in bags:
            print bag
