# coding: utf-8

from types import DictType, ListType, StringType, IntType
from fabkit import databag, env, conf
import commands


def decode_cluster_map():
    for cluster_name, data in env.cluster_map.items():
        env.cluster_map[cluster_name] = decode_data(data)


def decode_data(data, origin_data=None, parent_key=None):
    if not origin_data:
        origin_data = data

    if type(data) is DictType:
        for key, value in data.items():
            if parent_key:
                data[key] = decode_data(value, origin_data, '{0}.{1}'.format(parent_key, key))
            else:
                data[key] = decode_data(value, origin_data, key)

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
                            try:
                                tmp_data = tmp_data[tmp_key]
                            except KeyError:
                                raise DecodeException(
                                    'KeyError: {0} of {1} is not found in follow data.\n{2}'.format(
                                        tmp_key, data, tmp_data))

                        tmp_data = decode_data(tmp_data, origin_data)
                        if type(tmp_data) is StringType:
                            result += tmp_data + splited_key[1]
                        elif type(tmp_data) is IntType:
                            result += str(tmp_data) + splited_key[1]
                        else:
                            return tmp_data
                    elif key.find('!-') == 0:
                        tmp_key = key[2:]
                        host_cmd = 'cd {0} && {1}'.format(conf.NODE_DIR, tmp_key)
                        result = commands.getstatusoutput(host_cmd)
                        if result[0] != 0:
                            print 'Failed cmd({0}): {1}'.format(result[0], host_cmd)
                            print result[1]
                            return []

                        hosts = result[1].split('\n')
                        return hosts
                    elif key.find('require ') == 0:
                        print '{0} is require value.'.format(parent_key)
                        print key[8:]
                        print
                        exit(0)
                    else:
                        result += databag.get(key) + splited_key[1]
                else:
                    result += value

            return result

    return data


class DecodeException(Exception):
    pass
