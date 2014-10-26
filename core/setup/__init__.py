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
def setup(option=None):
    if option == 'test':
        env.is_test = True

    node = env.node_map.get(env.host)
    if env.is_chef:
        node.update({'last_cook': '{0} [start]'.format(util.get_timestamp())})
        util.dump_node()
    else:
        node.update({'last_fabcooks': ['{0} [start]'.format(util.get_timestamp())]})
        util.dump_node()

    if not check():
        log.warning('Failed to check(ssh)')
        return

    if env.is_chef:
        cook_result = sudo('chef-client')
        node = util.load_node()
        last_cook = '{0} [{1}]'.format(util.get_timestamp(), cook_result.return_code)
        node.update({'last_cook': last_cook})

    else:
        run = __import__(conf.FABSCRIPT_MODULE, {}, {}, [])

        last_fabcooks = []
        for fab_script in node.get('fabrun_list', []):
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
            node.update({'last_fabcooks': last_fabcooks})

    util.dump_node()
