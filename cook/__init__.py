# coding: utf-8

from fabric.api import task, env, settings, shell_env, parallel, cd
import conf, util
from api import *

@task
@parallel(pool_size=10)
def cook(option=None):
    with shell_env(PASSWORD=env.password):
        if not conf.is_server(option):
            run('rm -rf chef-solo')
            local('scp ~/chef-solo.tar.gz %s:~/' % (env.host))
            run('tar -xvf chef-solo.tar.gz')

        cmd_chef_solo = 'chef-solo -c chef-solo/solo.rb -j chef-solo/%s.json' % env.host
        cmd_chef_client = 'chef-client'

        if conf.is_proxy(option):
            with shell_env(http_proxy=conf.http_proxy, https_proxy=conf.http_proxy):
                if conf.is_server(option):
                    cook = sudo(cmd_chef_client, warn_only=True)
                else:
                    cook = sudo(cmd_chef_solo, warn_only=True)
        else:
            if conf.is_server(option):
                cook = sudo(cmd_chef_client, warn_only=True)
            else:
                cook = sudo(cmd_chef_solo, warn_only=True)

        last_cook = '%s[%d]' % (util.get_timestamp(), cook.return_code)

    uptime = run('uptime')

    host_json = util.load_json()
    host_json.update({'last_cook': last_cook})
    host_json.update({'uptime': uptime})
    util.dump_json(host_json)
