from fabric.api import task, env, warn_only, parallel
from api import *
import util, conf
import re


@task
@parallel
def check():
    RE_IP = re.compile('PING .+ \((.+)\) .+\(.+\) bytes')

    cmd_ping = 'ping %s -c 1 -W 2' % env.host
    cmd_ssh  = 'ssh %s hostname' % env.host

    ipaddress = 'failed'
    ssh       = 'failed'
    uptime    = ''

    with warn_only():
        host_json = util.load_json()
        result = cmd(cmd_ping, True)
        if result[0] == 0:
            if not env.is_test:
                ipaddress = RE_IP.findall(result[1])[0]

            result = cmd(cmd_ssh, True)
            if result[0] == 0:
                ssh = 'success'
                uptime = run('uptime')

        host_json.update({'ipaddress': ipaddress})
        host_json.update({'ssh': ssh})
        host_json.update({'uptime': uptime})
        util.dump_json(host_json)

