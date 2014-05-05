# coding: utf-8

from fabric.api import env, task, settings, shell_env, parallel
import re, os, json, commands, datetime, sys
import conf, util
from api import *
from check import check

@task
@parallel(pool_size=10)
def prepare(option=None):
    if not check():
        print 'Failed to check(ssh)'
        return

    set_pass(conf.UUID, env.password, 'localhost')
    cmd_knife_bootstrap = 'cd {0} && knife bootstrap {1} -x {2} --ssh-password {3} --sudo --use-sudo-password {3}'.format(conf.CHEFREPO_DIR, env.host, env.user, util.get_pass(conf.UUID, 'localhost'))

    if conf.CHEF_RPM:
        if os.path.exists(conf.CHEF_RPM):
            local('scp {0} {1}:{2}'.format(conf.CHEF_RPM, env.host, conf.TMP_CHEF_RPM))

            with settings(ok_ret_codes=[0,1]):
                cmd_chef_install = 'yum install {0} -y'.format(conf.TMP_CHEF_RPM)
                if conf.is_proxy(option):
                    with shell_env(http_proxy=conf.HTTP_PROXY, https_proxy=conf.HTTP_PROXY):
                        cmd_knife_bootstrap += ' --bootstrap-proxy {0}'.format(conf.HTTP_PROXY)
                        sudo(cmd_chef_install)
                        if conf.is_server(option):
                            local(cmd_knife_bootstrap)
                else:
                    sudo(cmd_chef_install)
                    if conf.is_server(option):
                        local(cmd_knife_bootstrap)
                run('rm -rf {0}'.format(conf.TMP_CHEF_RPM))
        else:
            print 'cannot access {0}'.format(conf.CHEF_RPM)
            return
    else:
        with shell_env(PASSWORD=env.password):
            local('knife solo prepare {0} --ssh-password {1}'.format(env.host, get_pass(conf.UUID, 'localhost')))
            if conf.is_server(option):
                local(cmd_knife_bootstrap)

    unset_pass('localhost')

    host_json = util.load_json()
    host_json.update({'last_cook': 'prepared'})
    util.dump_json(host_json)

    os.environ['PASSWORD'] = ''
