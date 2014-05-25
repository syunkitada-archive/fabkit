from fabric.api import task, env, warn_only, parallel
from api import *
import util, conf
import re


@task
@parallel(10)
def check():
    RE_IP = re.compile('PING .+ \((.+)\) .+\(.+\) bytes')

    cmd_ping = 'ping {0} -c 1 -W 2'.format(env.host)
    cmd_ssh  = 'ssh {0} hostname'.format(env.host)

    ipaddress = 'failed'
    ssh       = 'failed'
    uptime    = ''

    with warn_only():
        host_json = util.load_json()
        result = cmd(cmd_ping)
        if result[0] == 0:
            if not env.is_test:
                ipaddress = RE_IP.findall(result[1])[0]

            result = cmd(cmd_ssh)
            if result[0] == 0:
                ssh = 'success'
                uptime = run('uptime')

        host_json.update({'ipaddress': ipaddress})
        host_json.update({'ssh': ssh})
        host_json.update({'uptime': uptime})
        host_json.update({'last_check': util.get_timestamp()})
        util.dump_json(host_json)

        if ssh == 'success':
            return True
        else:
            return False

