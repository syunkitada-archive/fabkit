# coding: utf-8

import commands
import re
import os
from fabric import api
from lib import log

# memo
# with settings(warn_only=True): をやろうとすると失敗する (sudo: export command not found)
# warn_onlyを利用する場合は、run(cmd, warn_only=True) でやる


def cmd(cmd):
    log_cmd = 'cmd> ' + cmd
    log.info(log_cmd)

    if api.env.is_test:
        api.env.cmd_history.append(log_cmd)
        result = (0, cmd)
    else:
        result = commands.getstatusoutput(cmd)
    log.info('return> {0[0]}  out>\n{0[1]}'.format(result))
    return result


def run(cmd, **kwargs):
    log_cmd = 'run> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        result = api.run(cmd, kwargs)

    log.info('return> {0}  out>\n{1}'.format(result.return_code, result))
    return result


def sudo(cmd, **kwargs):
    log_cmd = 'sudo> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        result = api.sudo(cmd, kwargs)
    log.info('return> {0}  out>\n{1}'.format(result.return_code, result))
    return result


def local(cmd, **kwargs):
    log_cmd = 'local> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log.info(log_cmd)

    if api.env.is_test:
        result = test_cmd(cmd)
    else:
        result = api.local(cmd, kwargs)
    log.info('return> {0}'.format(result.return_code))
    return result


def local_scp(from_path, to_path, use_env_host=True):
    if use_env_host:
        return local('scp -o "StrictHostKeyChecking=no" {0} {1}:{2}'.format(from_path,
                                                                            api.env.host, to_path))
    else:
        return local('scp -o "StrictHostKeyChecking=no" {0} {1}'.format(from_path, to_path))


def scp(from_path, to_path):
    return run('scp -o "StrictHostKeyChecking=no" %s %s' % (from_path, to_path))


def test_cmd(cmd):
    if cmd == 'uptime':
        result = commands.getoutput('uptime')
    else:
        result = cmd
    return TestCmd(result)


class TestCmd(str):
    return_code = 0


# コマンド内に直接パスワードを書き込みたくない場合に利用する
# ログにパスワードが出力されるのを回避できる
# ファイルを通してパスワードを参照するようにする
def set_pass(key, password, host=None):
    secret_file = get_tmp_secret_file(host)

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
        local_scp(secret_file, '{0}:{1}'.format(host, secret_file))


def get_pass(key, host=None):
    secret_file = get_tmp_secret_file(host)
    return "`grep '^{0} ' {1} | awk '{{print $2;}}'`".format(key, secret_file)


def unset_pass(host=None):
    secret_file = get_tmp_secret_file(host)
    cmd('rm -f {0}'.format(secret_file))
    if not host:
        host = api.env.host
    if host != 'localhost':
        run('rm -f {0}'.format(secret_file))


def get_tmp_secret_file(host=None):
    if not host:
        host = api.env.host
    return os.path.expanduser('~/.{0}.secret'.format(host))
