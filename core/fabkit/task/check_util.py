# coding:utf-8

import re
import platform
from fabkit import api, env, run, cmd, status, log


re_ubuntu = re.compile('Ubuntu')
re_centos = re.compile('CentOS')
re_centos7 = re.compile('CentOS 7.*')

if platform.platform().find('CYGWIN') >= 0:
    # Because it can not be used cygwin of ping, use the ping of windows.
    # % ping 192.168.11.43
    # ping: socket: Operation not permitted
    # Use PING of Windows
    cmd_ping = 'PING {0} -n 1 -w 2'
else:
    cmd_ping = 'ping {0} -c 1 -W 2'


def check_basic():
    if env.is_test:
        ip = {
            'default': {
                'ip': '192.168.1.1',
                'dev': 'eth0',
            },
            'eth0': {
                'ip': '127.0.0.1',
                'dev': 'eth0',
            },
            'default_dev': {
                'ip': '127.0.0.1',
                'dev': 'eth0',
            },
        }
        env.node['ip'] = ip

        env.node['os'] = 'CentOS 7'
        env.node['package_manager'] = 'yum'
        env.node['service_manager'] = 'systemd'

        return {
            'msg': status.SUCCESS_CHECK_MSG,
            'task_status': status.SUCCESS,
        }

    # Check ping
    result = cmd(cmd_ping.format(env.host))
    if result[0] != 0:
        log.warning(status.FAILED_CHECK_PING_MSG)
        return {
            'msg': status.FAILED_CHECK_PING_MSG,
            'task_status': status.FAILED_CHECK_PING,
        }

    # Set IP
    if not set_ip():
        log.warning(status.FAILED_CHECK_SSH_MSG)
        return {
            'msg': status.FAILED_CHECK_SSH_MSG,
            'task_status': status.FAILED_CHECK_SSH,
        }

    if not set_os():
        log.warning(status.FAILED_CHECK_OS_MSG)
        return {
            'msg': status.FAILED_CHECK_OS_MSG,
            'task_status': status.FAILED_CHECK_OS,
        }

    log.info(status.SUCCESS_CHECK_MSG)
    return {
        'msg': status.SUCCESS_CHECK_MSG,
        'task_status': status.SUCCESS,
    }


def set_ip():
    with api.warn_only():
        result = run('ip r')
        if result.return_code == 0:
            devs = re.findall(
                '([0-9./]+) +dev +([a-zA-Z0-9\-]+) +proto +kernel +scope +link +src +([0-9.]+)',
                result)
            default = re.findall(
                'default +via +([0-9.]+) +dev +([a-zA-Z0-9\-]+) +.+', result)
            ips = {
                'default': {
                    'ip': default[0][0],
                    'dev': default[0][1],
                }
            }
            for dev in devs:
                ip_data = {
                    'subnet': dev[0],
                    'dev': dev[1],
                    'ip': dev[2],
                }
                ips[dev[0]] = ip_data
                ips[dev[1]] = ip_data
                ips[dev[0].split('.')[0]] = ip_data

            ips['default_dev'] = ips[ips['default']['dev']]

            env.node['ip'] = ips

            return True

        else:
            return False


def set_os():
    with api.warn_only():
        result = run('cat /etc/os-release')
        if result.return_code == 0:
            # CentOS(Test: Ubuntu 14.10, Centos Linux 7 (Core))
            re_search = re.search('PRETTY_NAME="(.+)"', result)
            os = re_search.group(1)
            env.node['os'] = os
            if re_ubuntu.match(os):
                env.node['package_manager'] = 'apt'
                env.node['service_manager'] = 'initd'
            if re_centos.match(os):
                env.node['package_manager'] = 'yum'
                env.node['service_manager'] = 'systemd'
        else:
            result = run('cat /etc/centos-release')
            if result.return_code == 0:
                # CentOS(Test: CentOS 6.5)
                re_search = re.search('release ([0-9.]+) ', result)
                os = 'CentOS {0}'.format(re_search.group(1))
                env.node['os'] = os
                env.node['package_manager'] = 'yum'
                env.node['service_manager'] = 'initd'
            else:
                if run('which yum').return_code == 0:
                    env.node['package_manager'] = 'yum'
                env.node['service_manager'] = 'initd'

    if 'os' in env.node:
        return True
    else:
        return False
