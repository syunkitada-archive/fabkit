# coding:utf-8

import re
import platform
from fabkit import api, env, run, cmd, status, log


if platform.platform().find('CYGWIN') >= 0:
    RE_IP = re.compile('.+\[(.+)\].+')
    cmd_ping = 'ping {0} -n 1 -w 2'
else:
    RE_IP = re.compile('PING .+ \((.+)\) .+\(.+\) bytes')
    cmd_ping = 'ping {0} -c 1 -W 2'


def check_basic():
    ip = 'failed'
    ssh = 'failed'
    uptime = ''
    result = {
        'msg': status.FAILED_CHECK_MSG,
        'task_status': status.FAILED_CHECK,
    }

    with api.warn_only():
        node = env.node
        if env.is_test:
            ip = '127.0.0.1'
            uptime = '12:00:00 up 5 days, 12:00,  1 user,  load average: 0.00, 0.00, 0.00'
            ssh = 'success'
            result = {
                'msg': status.SUCCESS_CHECK_MSG,
                'task_status': status.SUCCESS,
            }
        else:
            result = cmd(cmd_ping.format(env.host))
            if result[0] == 0:
                ip = RE_IP.findall(result[1])[0]
                uptime = run('uptime')
                ssh = 'success'

                log.info(status.SUCCESS_CHECK_MSG)
                result = {
                    'msg': status.SUCCESS_CHECK_MSG,
                    'task_status': status.SUCCESS,
                }
            else:
                log.warning(status.FAILED_CHECK_PING_MSG)
                result = {
                    'msg': status.FAILED_CHECK_PING_MSG,
                    'task_status': status.FAILED_CHECK_PING,
                }

        node.update({
            'ip': ip,
            'ssh': ssh,
            'uptime': uptime,
        })

        return result
