# coding: utf-8

import os
import yaml
import re
from fabkit import env
from oslo_config import cfg

CONF = cfg.CONF
RE_UPTIME = re.compile('^.*up (.+),.*user.*$')


def get_datamap(key):
    datamap_dir = os.path.join(CONF._node_dir, env.cluster['name'], CONF._datamap_dir)
    if not os.path.exists(datamap_dir):
        return None

    datamap_yml = os.path.join(datamap_dir, key + '.yml')
    if not os.path.exists(datamap_yml):
        return None

    with open(datamap_yml) as f:
        datamap = yaml.load(f)

    return datamap


def print_datamap(key):
    datamap = get_datamap(key)

    def _print_table(datamap):
        sorted_keys = sorted(datamap['data'][0].keys())

        rows = []
        key_row = []
        for key in sorted_keys:
            key_row.append(key.replace('!', ''))
        rows.append(key_row)

        for row in datamap['data']:
            tmp_row = []
            for key in sorted_keys:
                tmp_data = row[key]
                tmp_row.append(tmp_data)
            rows.append(tmp_row)

        max_len_rows = [None] * len(sorted_keys)
        for i, key in enumerate(sorted_keys):
            max_len_rows[i] = max([len(str(value[i])) for value in rows])

        format_str = ''
        for i, max_len_row in enumerate(max_len_rows):
            format_str += '{' + str(i) + ':<' + str(max_len_row) + '} '

        horizontal_line = '-' * (sum(max_len_rows) + len(max_len_rows))
        print horizontal_line
        print datamap['name']
        print horizontal_line
        for row in rows:
            print(format_str.format(*row))
        print horizontal_line

    if datamap is None:
        print('datamap "{0}" is not found.'.format(key))
        return

    if datamap['type'] == 'table':
        _print_table(datamap)

    elif datamap['type'] == 'multi-table':
        sorted_keys = sorted(datamap['data'][0].keys())

        keys = []
        prefix = ''
        for key in sorted_keys:
            if key.find('!!host') == 0:
                prefix += key
            else:
                keys.append(key)

        tmp_data = []
        for data in datamap['data']:
            for key in keys:
                tmp_row = {
                    '!!host': data['!!host'],
                    '!job': key,
                }
                tmp_row.update(data[key])
                tmp_data.append(tmp_row)

        tmp_datamap = {
            'name': datamap['name'],
            'data': tmp_data,
        }
        _print_table(tmp_datamap)


def dump_datamap(data_map):
    datamap_dir = os.path.join(CONF._node_dir, env.cluster['name'], CONF._datamap_dir)
    if not os.path.exists(datamap_dir):
        os.mkdir(datamap_dir)

    for map_name, map_data in data_map.items():
        datamap_yml = os.path.join(datamap_dir, map_name + '.yml')
        if os.path.exists(datamap_yml):
            with open(datamap_yml, 'r') as f:
                tmp_map_data = yaml.load(f)
                print data_map
                if tmp_map_data['type'] in ['table', 'multi-table', 'line-chart']:
                    new_data = map_data['data']
                    keys = [d['!!host'] for d in new_data]
                    ex_keys = [d['name'] for d in map_data.get('ex_data', [])]
                    for d in tmp_map_data['data']:
                        if d['!!host'] in ex_keys:
                            continue

                        if d['!!host'] not in keys:
                            new_data.append(d)
                            keys.append(d['!!host'])
                    tmp_map_data['data'] = new_data

                    if tmp_map_data['type'] == 'line-chart':
                        tmp_map_data['ex_data'] = map_data['ex_data']
                        tmp_map_data['layout'] = map_data['layout']

                else:
                    tmp_map_data['data'].update(map_data['data'])

                map_data = tmp_map_data

        if map_data['type'] == 'line-chart':
            data = map_data['data']
            ex_data = map_data.get('ex_data', [])
            new_data = []
            for ex in ex_data:
                x = []
                y = []
                if ex['x'] == 'data_0_x':
                    x = data[0]['x']
                if ex['y'] == 'sum(y)':
                    y = [0] * len(data[0]['y'])
                    for i, yd in enumerate(y):
                        sum = 0
                        for d in data:
                            sum += d['y'][i]

                        y[i] = sum

                tmp = {
                    '!!host': ex['name'],
                    'x': x,
                    'y': y,
                }
                new_data.append(tmp)

            keys = [d['!!host'] for d in new_data]
            for data in map_data['data']:
                if data['!!host'] not in keys:
                    new_data.append(data)
                    keys.append(data['!!host'])

            map_data['data'] = new_data

        with open(datamap_yml, 'w') as f:
            yaml.dump(map_data, f)
