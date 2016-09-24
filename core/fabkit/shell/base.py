# coding: utf-8

import commands
import re
import os
import time
from fabkit import api, log, env
from oslo_config import cfg

CONF = cfg.CONF


def cmd(cmd_str, retry_ttl=0, retry_interval=3):
    log_cmd = 'cmd> ' + cmd_str
    log.info(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        api.env.cmd_history.append(log_cmd)
        result = (0, cmd_str)
    else:
        result = commands.getstatusoutput(cmd_str)
        if result[0] != 0:
            log.info('failed cmd: {0}, ttl: {1}, sleep: {2}'.format(
                cmd_str, retry_ttl, retry_interval))
            if retry_ttl > 0:
                time.sleep(retry_interval)
                cmd(cmd_str, retry_ttl - 1, retry_interval)

    result_msg = 'return> {0[0]}  out>\n{0[1]}'.format(result)
    log.info(result_msg)
    print_for_test(result_msg)

    return result


def run(cmd, retry_ttl=0, retry_interval=3, **kwargs):
    log_cmd = 'run> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.debug(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        if env.is_local:
            result = local(cmd)
        else:
            result = api.run(cmd, **kwargs)

    result_msg = 'return> {0}  out>\n{1}'.format(result.return_code, result)
    log.debug(result_msg)
    print_for_test(result_msg)

    return result


def sudo(cmd, retry_ttl=0, retry_interval=3, **kwargs):
    log_cmd = 'sudo> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.debug(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        if env.is_local:
            result = local('sudo ' + cmd)
        else:
            result = api.sudo(cmd, **kwargs)

    result_msg = 'return> {0}  out>\n{1}'.format(result.return_code, result)
    log.debug(result_msg)
    print_for_test(result_msg)

    return result


def local(cmd, retry_ttl=0, retry_interval=3, capture=True, **kwargs):
    log_cmd = 'local> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        result = api.local(cmd, capture=capture, **kwargs)

    result_msg = 'return> {0}'.format(result.return_code)
    log.info(result_msg)
    print_for_test(result_msg)

    return result


def expect(cmd, expects=[], timeout=10, is_local=False, user=None):
    expect_cmd = ''
    for expect in expects:
        expect_cmd += '''
expect "{0}"
send "{1}"
        '''.format(expect[0], expect[1])

    cmd = '''expect -c '
set timeout {0}
spawn {1}
{2}
interact
'
'''.format(timeout, cmd, expect_cmd)

    if is_local:
        return local(cmd)
    else:
        if user is not None:
            return sudo(cmd, user=user)
        else:
            return run(cmd)


def reboot(wait=60):
    log_cmd = 'reboot> wait={0}'.format(wait)
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        result = test_cmd('uptime')
    else:
        api.reboot(wait=wait)
        result = api.run('uptime')

    result_msg = 'return> {0}  out>\n{1}'.format(result.return_code, result)
    log.info(result_msg)


def test_cmd(cmd):
    if cmd == 'uptime':
        result = commands.getoutput('uptime')
    else:
        result = cmd
    return TestCmd(result)


class TestCmd(str):
    return_code = 0


""" パスワード支援機能
コマンド内に直接パスワードを書き込みたくない場合に利用する
ログ出力にパスワードが出力されるのを回避できる

set_pass('test', 'hogepass')
set_pass('test', 'piyohogepass')
run('echo {0}'.format(get_pass('test')))
unset_pass()
"""


def set_pass(key, password, host=None):
    """
    ユーザホームのローカルファイルにパスワードを書き込む
    権限は600 user:user とする
    """
    secret_file = __get_local_secret_file(host)

    re_key = re.compile('^%s .+$' % key)
    replaced_file = ''
    exists_key = False

    if os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            for line in f:
                if re_key.match(line):
                    replaced_file += re_key.sub('{0} {1}'.format(key, password), line)
                    exists_key = True
                else:
                    replaced_file += line

    if not exists_key:
        replaced_file += '{0} {1}\n'.format(key, password)

    with open(secret_file, 'w') as f:
        f.write(replaced_file)

    if not host:
        host = api.env.host
    if host != 'localhost':
        path = __get_remote_secret_file(host)
        from transfer import scp
        scp(secret_file, path)
        run('chmod 600 {0}'.format(path))


def get_pass(key, host=None):
    secret_file = __get_remote_secret_file(host)
    return "`grep '^{0} ' {1} | awk '{{print $2;}}'`".format(key, secret_file)


def unset_pass(host=None):
    cmd('rm -f {0}'.format(__get_local_secret_file()))
    if not host:
        host = api.env.host
    if host != 'localhost':
        run('rm -f {0}'.format(__get_remote_secret_file()))


def __get_remote_secret_file(host=None):
    if not host:
        host = api.env.host
    return os.path.join('~/.{0}.secret'.format(host))


def __get_local_secret_file(host=None):
    if not host:
        host = api.env.host
    return os.path.join(CONF._tmp_dir, '.{0}.secret'.format(host))


def print_for_test(msg, host=None):
    if api.env.is_test:
        if not host:
            host = api.env.host

        print '[{0}] {1}'.format(host, msg)
