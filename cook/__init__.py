# coding: utf-8

from fabric.api import task, env, settings, shell_env, parallel, cd, hide
import conf, util
from api import *
from check import check

@task
@parallel(pool_size=10)
def fabcook(option=None):
    host_json = util.load_json()
    run = __import__(conf.FABSCRIPT_MODULE, {}, {}, [])

    last_fabcooks = []
    for fab_script in host_json.get('fab_run_list', []):
        modules = fab_script.split('.')
        module = run

        i = 0
        len_modules = len(modules)
        while i < len_modules:
            module = getattr(module, modules[i])
            i += 1

        return_code = module()

        last_fabcooks.append('{0} [{1}:{2}]'.format(util.get_timestamp(), fab_script, return_code))

    host_json.update({'last_fabcooks': last_fabcooks})
    util.dump_json(host_json)

@task
@parallel(pool_size=10)
def cook(option=None):
    if not check():
        print 'Failed to check(ssh)'
        return

    if not conf.is_server(option):
        run('rm -rf chef-solo')
        local_scp('~/chef-solo.tar.gz', '{0}:~/'.format(env.host))
        with hide('output'):
            run('tar -xvf chef-solo.tar.gz')
        run('rm -f chef-solo.tar.gz')
        run('echo \'{0}\' > chef-solo/solo.json'.format(conf.get_jsonstr_for_chefsolo()))

    cmd_chef_solo = 'chef-solo -c chef-solo/solo.rb -j chef-solo/solo.json'
    cmd_chef_client = 'chef-client'

    if conf.is_proxy(option):
        with shell_env(http_proxy=conf.HTTP_PROXY, https_proxy=conf.HTTPS_PROXY):
            if conf.is_server(option):
                cook = sudo(cmd_chef_client, warn_only=True)
            else:
                cook = sudo(cmd_chef_solo, warn_only=True)
    else:
        if conf.is_server(option):
            cook = sudo(cmd_chef_client, warn_only=True)
        else:
            cook = sudo(cmd_chef_solo, warn_only=True)

    host_json = util.load_json()
    last_cook = '{0} [{1}]'.format(util.get_timestamp(), cook.return_code)
    host_json.update({'last_cook': last_cook})
    util.dump_json(host_json)
