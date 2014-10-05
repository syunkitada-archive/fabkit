# coding: utf-8

from fabric.api import (task,
                        env,
                        parallel,)
from lib import conf
from lib import util
from lib import log
from lib.api import sudo
from check import check


@task
@parallel(pool_size=10)
def cook(option=None):
    attr = env.host_attrs[env.host]
    if env.is_chef:
        attr.update({'last_cook': '{0} [start]'.format(util.get_timestamp())})
        util.dump_json()
    else:
        attr.update({'last_fabcooks': ['{0} [start]'.format(util.get_timestamp())]})
        util.dump_json()

    if not check():
        log.warning('Failed to check(ssh)')
        return

    if env.is_chef:
        cook_result = sudo('chef-client')
        attr = util.load_json()
        last_cook = '{0} [{1}]'.format(util.get_timestamp(), cook_result.return_code)
        attr.update({'last_cook': last_cook})

    else:
        run = __import__(conf.FABSCRIPT_MODULE, {}, {}, [])

        last_fabcooks = []
        for fab_script in attr.get('fab_run_list', []):
            modules = fab_script.split('.')
            module = run

            i = 0
            len_modules = len(modules)
            while i < len_modules:
                module = getattr(module, modules[i])
                i += 1

            return_code = module()

            last_fabcooks.append('{0} [{1}:{2}]'.format(util.get_timestamp(),
                                                        fab_script, return_code))
            attr.update({'last_fabcooks': last_fabcooks})

    util.dump_json()
