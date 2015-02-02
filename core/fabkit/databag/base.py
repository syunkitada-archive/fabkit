# coding: utf-8

import re
import os
import yaml
from fabkit import conf, cmd


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
    data_file = os.path.join(conf.DATABAG_DIR, data_file)
    key = splited_key[1]
    return key, data_file


from types import StringType, DictType, ListType


def decode_data(data, origin_data=None):
    if not origin_data:
        origin_data = data

    if type(data) is DictType:
        for key, value in data.items():
            data[key] = decode_data(value, origin_data)

    if type(data) is ListType:
        data = [decode_data(value, origin_data) for value in data]

    if type(data) is StringType:
        splited_value = data.split('$(')
        if len(splited_value) > 1:
            result = ''
            for value in splited_value:
                splited_key = value.split(')', 1)
                if len(splited_key) > 1:
                    key = splited_key[0]
                    if key.find('#') == 0:
                        tmp_keys = key[1:].split('.')
                        tmp_data = origin_data
                        for tmp_key in tmp_keys:
                            if tmp_key.isdigit():
                                tmp_key = int(tmp_key)
                            tmp_data = tmp_data[tmp_key]

                        tmp_data = decode_data(tmp_data, origin_data)
                        if type(tmp_data) is StringType:
                            result += tmp_data + splited_key[1]
                        else:
                            return tmp_data

                    else:
                        result += get(key) + splited_key[1]
                else:
                    result += value

            return result

    return data


def print_list(key=None):
    if key:
        path = os.path.join(conf.DATABAG_DIR, key)
    else:
        path = conf.DATABAG_DIR

    output = cmd('find {0}'.format(path))
    RE_DATABAG_YAML = re.compile('{0}/(.*).yaml'.format(conf.DATABAG_DIR))
    bags = RE_DATABAG_YAML.findall(output[1])
    if len(bags) == 0:
        print 'Databag was not found.'
    else:
        for bag in bags:
            print bag
