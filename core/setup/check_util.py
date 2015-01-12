# coding:utf-8

from fabric.api import task, env, warn_only, parallel
from lib.api import run, cmd
from lib import util
from lib import conf
import yaml
import re
import platform
import os


if platform.platform().find('CYGWIN') >= 0:
    RE_IP = re.compile('.+\[(.+)\].+')
    cmd_ping = 'ping {0} -n 1 -w 2'
else:
    RE_IP = re.compile('PING .+ \((.+)\) .+\(.+\) bytes')
    cmd_ping = 'ping {0} -c 1 -W 2'

RE_NODE = re.compile('log/(.+)/status.json: +"(.+)"')


@task
@parallel(10)
def check_basic():
    ip = 'failed'
    ssh = 'failed'
    uptime = ''

    if len(env.hosts) == 0:
        print 'host: error'
        print '-' * 40
        re_host = re.compile('{0}/(.+)/status.yaml'.format(conf.LOG_DIR))

        for root, dirs, files in os.walk(conf.LOG_DIR):
            for file in files:
                if file.find('status.yaml') == 0:
                    path = os.path.join(root, file)
                    with open(path) as f:
                        status = yaml.load(f)
                        if status['ipaddress'] == 'failed' or \
                                status['ssh'] == 'failed':
                            # TODO check last_fabcooks, last_cook
                            host = re_host.search(path).group(1)
                            print '{0}: {1}'.format(host, status)

        return

    with warn_only():
        node = env.node_map.get(env.host)
        if env.is_test:
            ip = '127.0.0.1'
            uptime = '12:00:00 up 5 days, 12:00,  1 user,  load average: 0.00, 0.00, 0.00'
            ssh = 'success'
        else:
            result = cmd(cmd_ping.format(env.host))
            ip = RE_IP.findall(result[1])[0]
            if result[0] == 0:
                uptime = run('uptime')
                ssh = 'success'

        node.update({'ip': ip})
        node.update({'ssh': ssh})
        node.update({'uptime': uptime})
        node.update({'last_check': util.get_timestamp()})
        util.dump_node(node=node)

        if ssh == 'success':
            return True
        else:
            return False
