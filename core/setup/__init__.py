# coding: utf-8

from fabric.api import (task,
                        env,
                        parallel,)
from lib import conf, util, log
from lib.api import sudo, db, filer
from check import check
from types import IntType, TupleType


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
        filer.mkdir(conf.REMOTE_DIR)
        filer.mkdir(conf.STORAGE_DIR)
        filer.mkdir(conf.TMP_DIR, mode='777')

        for fabscript in node.get('fabruns', []):
            db.setuped(-1, 'start setup', script_name=fabscript)
            script = '.'.join((conf.FABSCRIPT_MODULE, fabscript))
            module = __import__(script, {}, {}, 'setup')
            func = getattr(module, 'setup')
            result = func()

            status = None
            msg = None
            if type(result) is IntType:
                status = result
            if type(result) is TupleType:
                status, msg = result
            if not status:
                status = 0
            if not msg:
                msg = 'end setup'

            db.setuped(status, msg, script_name=fabscript)

    util.dump_node()
