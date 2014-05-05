# coding: utf-8

from fabric import api
import commands, re, os
import conf, util

# memo
# with settings(warn_only=True): をやろうとすると失敗する (sudo: export command not found)
# warn_onlyを利用する場合は、run(cmd, warn_only=True) でやる

def cmd(cmd, is_get_status=False):
    log_cmd = 'cmd> ' + cmd
    log(log_cmd)
    if api.env.is_test:
        api.env.cmd_history.append(log_cmd)
        if is_get_status:
            return (0, cmd)
        return cmd
    else:
        if is_get_status:
            return commands.getstatusoutput(cmd)
        return commands.getoutput(cmd)

def run(cmd, **kwargs):
    log_cmd = 'run> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log(log_cmd)

    if api.env.is_test:
        return test_cmd(cmd)
    else:
        return api.run(cmd, kwargs)

def sudo(cmd, **kwargs):
    log_cmd = 'sudo> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log(log_cmd)

    if api.env.is_test:
        return test_cmd(cmd)
    else:
        return api.sudo(cmd, kwargs)

def local(cmd, **kwargs):
    log_cmd = 'local> ' + cmd
    api.env.cmd_history.append(log_cmd)
    log(log_cmd)

    if api.env.is_test:
        return test_cmd(cmd)
    else:
        return api.local(cmd, kwargs)

def local_scp(from_path, to_path):
    return local('scp -o "StrictHostKeyChecking=no" %s %s' % (from_path, to_path))

def scp(from_path, to_path):
    return run('scp -o "StrictHostKeyChecking=no" %s %s' % (from_path, to_path))

def log(msg):
    with open('%s/%s.log' % (conf.LOG_DIR, api.env.host), 'a') as f:
        f.write('%s: %s\n' % (util.get_timestamp(), msg))


def test_cmd(cmd):
    if cmd == 'uptime':
        result = commands.getoutput('uptime')
    else:
        result = cmd
    return TestCmd(result)

class TestCmd(str):
    return_code = 0

# コマンド内に直接パスワードを書き込みたくない場合に利用
# ファイルを通してパスワードを参照するようにする
def set_pass(key, password, is_local=False):
    password_file = conf.get_tmp_password_file(is_local)
    re_key = re.compile('^%s .+$' % key)
    replaced_file = ''
    exists_key = False
    if os.path.exists(password_file):
        with open(password_file, 'r') as f:
            for line in f:
                if re_key.match(line):
                    replaced_file += re_key.sub('{0} {1}'.format(key, password), line)
                    exists_key = True
                else:
                    replaced_file += line

    if not exists_key:
        replaced_file += '{0} {1}\n'.format(key, password)

    with open(password_file, 'w') as f:
        f.write(replaced_file)

    if not is_local:
        local_scp(password_file, '{0}:{1}'.format(api.env.host, password_file))

def get_pass(key, is_local=False):
    password_file = conf.get_tmp_password_file(is_local)
    return "`grep '^{0} ' {1} | awk '{{print $2;}}'`".format(key, password_file)

def unset_pass(is_local=False):
    password_file = conf.get_tmp_password_file()
    cmd('rm -f {0}'.format(password_file))
    if not is_local:
        run('rm -f {0}'.format(api.env.tmp_password_file))
