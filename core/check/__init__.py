from fabric.api import task, env, warn_only, parallel
from lib.api import run, cmd
from lib import util
from lib import conf
import re


RE_IP = re.compile('PING .+ \((.+)\) .+\(.+\) bytes')
RE_NODE = re.compile('log/(.+)/status.json: +"(.+)"')


@task
@parallel(10)
def check():
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

    cmd_ping = 'ping {0} -c 1 -W 2'.format(env.host)

    ipaddress = 'failed'
    ssh = 'failed'
    uptime = ''

    with warn_only():
        host_json = util.load_json()
        result = cmd(cmd_ping)
        if result[0] == 0:
            if not env.is_test:
                ipaddress = RE_IP.findall(result[1])[0]
            uptime = run('uptime')
            ssh = 'success'

        host_json.update({'ipaddress': ipaddress})
        host_json.update({'ssh': ssh})
        host_json.update({'uptime': uptime})
        host_json.update({'last_check': util.get_timestamp()})
        util.dump_json(host_json)

        if ssh == 'success':
            return True
        else:
            return False
