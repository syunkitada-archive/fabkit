# coding: utf-8

import json
from fabkit import env


def confirm(msg_ask, msg_cancel=None):
    if env.is_test:
        return True
    if raw_input('\n%s (y/n) ' % msg_ask) == 'y':
        return True
    else:
        if msg_cancel:
            print msg_cancel
        return False


def print_node_map(node_map=None, option=None):
    if not node_map:
        node_map = env.node_map

    if len(node_map) == 0:
        max_len_host = 10
    else:
        max_len_host = max([len(node['path']) for node in node_map.values()])

    if option:
        format_str = '{host:<' + str(max_len_host) + '} {status:<6} {logs}'
    else:
        format_str = '{host:<' + str(max_len_host) + '} {fabruns}'

    horizontal_line = '-' * (max_len_host + 30)
    print horizontal_line
    print format_str.format(host='host',
                            run_list='run_list',
                            status='status',
                            logs='logs',
                            fabruns='fabruns',)
    print horizontal_line

    nodes = sorted(node_map.items(), reverse=False)

    for node_tapple in nodes:
        node = node_tapple[1]
        host = node.get('path', '')
        if option == 'status' or option == 'error':
            status = node.status
            if option == 'error' and status == 0:
                continue

            logs = ''
            tmp_logs = json.loads(node.logs)
            last_log_i = len(tmp_logs) - 1
            for i, log in enumerate(tmp_logs):
                if log['status'] != 0:
                    logs += '\033[93m{0[fabscript]}: {0[msg]} [{0[status]}]\033[0m'.format(log)
                else:
                    logs += '{0[fabscript]}: {0[msg]} [{0[status]}]'.format(log)
                if not i == last_log_i:
                    logs += '\n' + (' ' * (max_len_host + 8))

        else:
            status = ''
            logs = ''

        run_list = node.get('run_list', [])
        fabruns = node.get('fabruns', [])

        print format_str.format(host=host,
                                run_list=run_list,
                                status=status,
                                logs=logs,
                                fabruns=fabruns,
                                )


def print_runs():
    runs = env.runs
    max_len_cluster = 7
    max_len_host = 7
    for run in runs:
        len_cluster = len(run['cluster'])
        if len_cluster > max_len_host:
            max_len_cluster = len_cluster

        for cluster_run in run['runs']:
            tmp_max_len_host = max([len(host) for host in cluster_run['hosts']])
            if max_len_host < tmp_max_len_host:
                max_len_host = tmp_max_len_host

    format_str = '{cluster:<' + str(max_len_cluster) + '} {host:<' \
        + str(max_len_host) + '} {fabscript}'

    horizontal_line = '-' * (max_len_cluster + max_len_host + 40)
    print horizontal_line
    print format_str.format(cluster='cluster', host='host', fabscript='fabscript')
    print horizontal_line

    for run in runs:
        cluster_status_map = env.cluster_map[run['cluster']]['__status']
        fabscript_status_map = cluster_status_map['fabscript_map']
        for cluster_run in run['runs']:
            fabscript_name = cluster_run['fabscript']
            fabscript = fabscript_status_map[fabscript_name]
            fabscript_str = '{0}: {1} > {2}'.format(
                fabscript_name, fabscript['status'], cluster_run['expected_status'])
            for host in cluster_run['hosts']:
                print format_str.format(cluster=run['cluster'],
                                        fabscript=fabscript_str,
                                        host=host)
