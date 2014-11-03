# coding: utf-8

import commands
import re
import os
from fabric import api
from lib import log
from lib import conf


def cmd(cmd):
    log_cmd = 'cmd> ' + cmd
    log.info(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        api.env.cmd_history.append(log_cmd)
        result = (0, cmd)
    else:
        result = commands.getstatusoutput(cmd)

    result_msg = 'return> {0[0]}  out>\n{0[1]}'.format(result)
    log.info(result_msg)
    print_for_test(result_msg)

    return result


def run(cmd, **kwargs):
    log_cmd = 'run> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        result = api.run(cmd, kwargs)

    result_msg = 'return> {0}  out>\n{1}'.format(result.return_code, result)
    log.info(result_msg)
    print_for_test(result_msg)

    return result


def sudo(cmd, **kwargs):
    log_cmd = 'sudo> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        result = api.sudo(cmd, kwargs)

    result_msg = 'return> {0}  out>\n{1}'.format(result.return_code, result)
    log.info(result_msg)
    print_for_test(result_msg)

    return result


def local(cmd, **kwargs):
    log_cmd = 'local> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)
    print_for_test(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        result = api.local(cmd, kwargs)

    result_msg = 'return> {0}'.format(result.return_code)
    log.info(result_msg)
    print_for_test(result_msg)

    return result


def scp(from_path, to_path, is_local=True, use_env_host=True):
    if is_local:
        if use_env_host:
            return local('scp -o "StrictHostKeyChecking=no" {0} {1}:{2}'.format(from_path,
                         api.env.host, to_path))
        else:
            return local('scp -o "StrictHostKeyChecking=no" {0} {1}'.format(from_path, to_path))
    else:
        return run('scp -o "StrictHostKeyChecking=no" %s %s' % (from_path, to_path))


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
    return os.path.join(conf.TMP_DIR, '.{0}.secret'.format(host))


def print_for_test(msg, host=None):
    if api.env.is_test:
        if not host:
            host = api.env.host

        print '[{0}] {1}'.format(host, msg)
