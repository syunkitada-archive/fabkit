# coding: utf-8

from fabric import api
import commands
import conf, util

api.env.cmd_history = []

# memo
# with settings(warn_only=True): をやろうとすると失敗する (sudo: export command not found)
# warn_onlyを利用する場合は、run(cmd, warn_only=True) でやる

def cmd(cmd):
    if api.env.is_test:
        api.env.cmd_history.append(cmd)
        return cmd
    else:
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

def log(msg):
    with open('%s/%s.log' % (conf.log_dir_path, api.env.host), 'a') as f:
        f.write('%s: %s\n' % (util.get_timestamp(), msg))

def test_cmd(cmd):
    if cmd == 'uptime':
        result = commands.getoutput('uptime')
    else:
        result = cmd
    return TestCmd(result)

class TestCmd(str):
    return_code = 0
