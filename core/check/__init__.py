# coding:utf-8

from fabric.api import task, env, warn_only, parallel
from lib.api import run, cmd
from lib import util
from lib import conf
import re
import platform


if platform.platform().find('CYGWIN') >= 0:
    RE_IP = re.compile('.+\[(.+)\].+')
    cmd_ping = 'ping {0} -n 1 -w 2'
else:
    RE_IP = re.compile('PING .+ \((.+)\) .+\(.+\) bytes')
    cmd_ping = 'ping {0} -c 1 -W 2'

RE_NODE = re.compile('log/(.+)/status.json: +"(.+)"')


@task
@parallel(10)
def check():
    ipaddress = 'failed'
    ssh = 'failed'
    uptime = ''

    if len(env.hosts) == 0:
        find_status = cmd('find {0} -name status.json'.format(conf.LOG_DIR))
        find_status = find_status[1].replace('\n', ' ')
        grep_cmd = 'grep -H \' \[.*:[^0]\]\' {0}'.format(find_status)
        warning_nodes = cmd(grep_cmd)[1]
        failed_ssh_nodes = cmd('grep \'"ssh": "failed"\' {0}'.format(find_status))[1]
        if warning_nodes == '' and failed_ssh_nodes == '':
            print 'No warning nodes.'
        else:
            nodes = {}

            fsnodes = RE_NODE.findall(failed_ssh_nodes)
            wnodes = RE_NODE.findall(warning_nodes)

            for fsnode in fsnodes:
                nodes.update({fsnode[0]: [fsnode[1]]})

            for wnode in wnodes:
                status = nodes.get(wnode[0], [])
                status.append(wnode[1])
                nodes.update({wnode[0]: status})

            for node in nodes:
                print '{0:<40} {1}'.format(node, nodes[node])

        return

    with warn_only():
        node = env.node_map[env.host]
        result = cmd(cmd_ping.format(env.host))

        if result[0] == 0:
            if not env.is_test:
                ipaddress = RE_IP.findall(result[1])[0]
            uptime = run('uptime')
            ssh = 'success'

        node.update({'ipaddress': ipaddress})
        node.update({'ssh': ssh})
        node.update({'uptime': uptime})
        node.update({'last_check': util.get_timestamp()})
        util.dump_node()

        if ssh == 'success':
            return True
        else:
            return False
