# coding: utf-8

import conf, util
from fabric.api import *
import commands

@task
@hosts('localhost')
def host(host_pattern=None):
    run('mkdir -p %s' % conf.chefric_path)

    env.hosts = util.get_available_hosts(host_pattern)

    if not env.is_test:
        print 'set up targets'
        for host in env.hosts:
            print host

        print '\nis ok?\nif you ok, enter your password\n'
        sudo('hostname')

        for task in env.tasks:
            if task.find('cook') != -1:
                with cd(conf.chef_repo_path):
                    with shell_env(PASSWORD=env.password):
                        run('knife solo cook localhost --no-berkshelf --no-chef-check --ssh-password $PASSWORD')
                run('cp -r %s/* chef-solo/' % conf.node_path)
                run('tar -czf chef-solo.tar.gz chef-solo')



