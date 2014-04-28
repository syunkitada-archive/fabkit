# coding: utf-8

from fabric.api import env, task, settings, shell_env, parallel
import re, os, json, commands, datetime, sys
import conf, util
from api import *

@task
@parallel(pool_size=5)
def prepare(option=None):
    if not env.host:
        print 'host has not been set.'
        print 'please run "host" task before "prepare" task.'
        return

    if conf.chef_rpm_path:
        if os.path.exists(conf.chef_rpm_path):
            local('scp %s %s:~/%s' % (conf.chef_rpm_path, env.host, conf.tmp_chef_rpm))

            with settings(ok_ret_codes=[0,1]):
                cmd = 'yum install %s -y' % conf.tmp_chef_rpm
                if conf.is_proxy(option):
                    with shell_env(http_proxy=conf.http_proxy, https_proxy=conf.http_proxy):
                        sudo(cmd)
                else:
                    sudo(cmd)
                run('rm -rf %s' % conf.tmp_chef_rpm)
        else:
            print 'cannot access %s' % conf.chef_rpm_path
            return
    else:
        with shell_env(PASSWORD=env.password):
            local('knife solo prepare %s --ssh-password $PASSWORD' % (env.host))

    uptime = run('uptime')

    host_json = util.load_json()
    host_json.update({'last_cook': 'prepared'})
    host_json.update({'uptime': uptime})
    util.dump_json(host_json)

