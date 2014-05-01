# coding: utf-8

from fabric.api import env, task, settings, shell_env, parallel
import re, os, json, commands, datetime, sys
import conf, util
from api import *

@task
@parallel(pool_size=10)
def prepare(option=None):
    if not env.host:
        print 'host has not been set.'
        print 'please run "host" task before "prepare" task.'
        return

    os.environ['PASSWORD'] = env.password
    cmd_knife_bootstrap = 'cd %s && knife bootstrap %s -x %s --ssh-password $PASSWORD --sudo --use-sudo-password $PASSWORD' % (conf.chef_repo_path, env.host, env.user)

    if conf.chef_rpm_path:
        if os.path.exists(conf.chef_rpm_path):
            local('scp %s %s:~/%s' % (conf.chef_rpm_path, env.host, conf.tmp_chef_rpm))

            with settings(ok_ret_codes=[0,1]):
                cmd_chef_install = 'yum install %s -y' % conf.tmp_chef_rpm
                if conf.is_proxy(option):
                    with shell_env(http_proxy=conf.http_proxy, https_proxy=conf.http_proxy):
                        cmd_knife_bootstrap += ' --bootstrap-proxy %s' % conf.http_proxy
                        sudo(cmd_chef_install)
                        if conf.is_server(option):
                            local(cmd_knife_bootstrap)
                else:
                    sudo(cmd_chef_install)
                    if conf.is_server(option):
                        local(cmd_knife_bootstrap)
                run('rm -rf %s' % conf.tmp_chef_rpm)
        else:
            print 'cannot access %s' % conf.chef_rpm_path
            return
    else:
        with shell_env(PASSWORD=env.password):
            local('knife solo prepare %s --ssh-password $PASSWORD' % (env.host))
            if conf.is_server(option):
                local(cmd_knife_bootstrap)

    uptime = run('uptime')

    host_json = util.load_json()
    host_json.update({'last_cook': 'prepared'})
    host_json.update({'uptime': uptime})
    util.dump_json(host_json)

    os.environ['PASSWORD'] = ''
