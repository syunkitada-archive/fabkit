# coding: utf-8

from fabric.api import (task,
                        env,
                        parallel)
from lib import conf, util, log
from lib.api import sudo, db, filer
from check import check
from types import IntType, TupleType


@task
def _setup(option=None):
    setup(option)


@task
@parallel(pool_size=10)
def setup(option=None):
    if option == 'test':
        env.is_test = True

    node = env.node_map.get(env.host)

    if not check():
        db.setuped(-1, 'Failed to check')
        log.warning('Failed to check')
        return

    if env.is_chef:
        result = sudo('chef-client')
        status = result.return_code
        if status == 0:
            msg = 'setuped'
        else:
            msg = 'error'

        db.setuped_chef(status, msg)

    else:
        filer.mkdir(conf.REMOTE_DIR)
        filer.mkdir(conf.STORAGE_DIR)
        filer.mkdir(conf.TMP_DIR, mode='777')

        db.setuped(-1, 'start setup', is_init=True)
        for fabscript in node.get('fabruns', []):
            db.create_fabscript(fabscript)
            util.update_log(fabscript, 1, 'start setup')
            db.setuped(-1, 'start {0}'.format(fabscript))

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

            util.update_log(fabscript, status, msg)
            db.setuped(status, msg)

            if status != 0:
                break

    util.dump_node()


@task
def _manage(*args):
    manage(args)


@task
@parallel(pool_size=10)
def manage(*args):
    if args[0] == 'test':
        env.is_test = True

    if not check():
        log.warning('Failed to check(ssh)')
        return

    node = env.node_map.get(env.host)
    filer.mkdir(conf.REMOTE_DIR)
    filer.mkdir(conf.STORAGE_DIR)
    filer.mkdir(conf.TMP_DIR, mode='777')

    for fabscript in node.get('fabruns', []):
        db.create_fabscript(fabscript)
        db.setuped(-1, 'start setup', script_name=fabscript)
        script = '.'.join((conf.FABSCRIPT_MODULE, fabscript))
        module = __import__(script, {}, {}, 'setup')

        status = 0
        msgs = []
        for arg in args:
            if hasattr(module, arg):
                func = getattr(module, arg)
                result = func()
                if type(result) is IntType:
                    status = result
                    msg = arg
                if type(result) is TupleType:
                    status, msg = result
                    msg = '{0}:{1}'.format(arg, msg)
                if not result:
                    status = 0
                    msg = arg

                msgs.append(msg)

                if status != 0:
                    break

        msg = 'end manage: [{0}]'.format(', '.join(msgs))

        db.setuped(status, msg, script_name=fabscript)

    util.dump_node()
