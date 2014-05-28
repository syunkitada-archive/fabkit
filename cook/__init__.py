# coding: utf-8

from fabric.api import task, env, settings, shell_env, parallel, cd, hide, serial
import conf, util, log
from api import *
from check import check

@task
@parallel(pool_size=10)
def cook(option=None):
    host_json = util.load_json()
    host_json.update({'last_cook': '{0} [start]'.format(util.get_timestamp())})
    util.dump_json(host_json)

    if not check():
        log.warning('Failed to check(ssh)')
        return

    if env.is_server:
        cook_cmd = 'chef-client'
        cook_prefix = 'client'

    else:
        run('rm -rf chef-solo')
        local_scp('~/chef-solo.tar.gz', '{0}:~/'.format(env.host))
        with hide('output'):
            run('tar -xvf chef-solo.tar.gz')
        run('rm -f chef-solo.tar.gz')
        run('echo \'{0}\' > chef-solo/solo.json'.format(conf.get_jsonstr_for_chefsolo()))
        cook_cmd = 'chef-solo -c chef-solo/solo.rb -j chef-solo/solo.json'
        cook_prefix = 'solo'

    if conf.is_proxy(option):
        with shell_env(http_proxy=conf.HTTP_PROXY, https_proxy=conf.HTTPS_PROXY):
            cook_result = sudo(cook_cmd)
    else:
            cook_result = sudo(cook_cmd)

    host_json = util.load_json()
    last_cook = '{0} [{1}:{2}]'.format(util.get_timestamp(), cook_prefix, cook_result.return_code)
    host_json.update({'last_cook': last_cook})
    util.dump_json(host_json)

@task
@parallel(pool_size=10)
def cookfab(option=None):
    host_json = util.load_json()
    host_json.update({'last_fabcooks': ['{0} [start]'.format(util.get_timestamp())]})
    util.dump_json(host_json)

    if not check():
        log.warning('Failed to check(ssh)')
        return

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
