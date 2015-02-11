# coding: utf-8

import os
import yaml
from fabkit import env, databag, conf
from node_model import update_cluster, update_node
from types import StringType, DictType, ListType


def update_all(status_code, msg):
    """
    Save status of node, fabscript to dababase and files.
    """

    for cluster_name, data in env.cluster_map.items():
        node_status_map = data['__status'].pop('node_map')
        cluster = update_cluster(cluster_name, data)
        env.cluster_map[cluster_name] = decode_data(data)
        data['__status']['node_map'] = node_status_map

        for host, status_data in node_status_map.items():
            path = '{0}/{1}'.format(cluster_name, host)
            update_node(status_code, msg,
                        path=path, cluster=cluster, data=status_data)

        print data['__status']['node_map']
        status_yaml = os.path.join(conf.NODE_DIR, cluster_name, '__status.yaml')
        with open(status_yaml, 'w') as f:
            f.write(yaml.dump({'__status': data['__status']}))


def decode_data(data, origin_data=None):
    if not origin_data:
        origin_data = data

    if type(data) is DictType:
        for key, value in data.items():
            data[key] = decode_data(value, origin_data)

    if type(data) is ListType:
        data = [decode_data(value, origin_data) for value in data]

    if type(data) is StringType:
        splited_value = data.split('${')
        if len(splited_value) > 1:
            result = ''
            for value in splited_value:
                splited_key = value.split('}', 1)
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
                        result += databag.get(key) + splited_key[1]
                else:
                    result += value

            return result

    return data
