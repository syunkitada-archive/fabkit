# coding: utf-8

from fabric.api import (task,
                        env,
                        parallel)
import inspect
from lib import conf, util, log
from lib.api import sudo, db, filer, status_code
from check_util import check_basic
from types import IntType, TupleType


@task
def _check(option=None):
    check(option)


@task
@parallel(pool_size=10)
def check(option=None):
    run_func('check', option)


@task
def _setup(option=None):
    setup(option)


@task
@parallel(pool_size=10)
def setup(option=None):
    run_func('setup', option)
    run_func('check', option)


def run_func(func_prefix, option=None):
    if option == 'test':
        env.is_test = True

    db.setuped(status_code.FABSCRIPT_STARTED, '{0} started'.format(func_prefix))

    node = env.node_map.get(env.host)

    if not check_basic():
        db.setuped(1, 'Failed to check')
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
        if func_prefix == 'setup':
            filer.mkdir(conf.REMOTE_DIR)
            filer.mkdir(conf.STORAGE_DIR)
            filer.mkdir(conf.TMP_DIR, mode='777')

        db.setuped(1, 'start setup', is_init=True)
        for fabscript in node.get('fabruns', []):
            db.create_fabscript(fabscript)
            util.update_log(fabscript, 1, 'start setup')
            db.setuped(1, 'start {0}'.format(fabscript))

            script = '.'.join((conf.FABSCRIPT_MODULE, fabscript))
            module = __import__(script, {}, {}, func_prefix)

            func_names = []
            for member in inspect.getmembers(module):
                if inspect.isfunction(member[1]):
                    if member[0].find(func_prefix) == 0:
                        func_names.append(member[0])

            func_names.sort()
            for func_name in func_names:
                func = getattr(module, func_name)
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
                    msg = 'end {0}'.format(func_prefix)

                util.update_log(fabscript, status, msg)
                db.setuped(status, msg)

                if status != 0:
                    break


@task
def _manage(*args):
    manage(args)


@task
@parallel(pool_size=10)
def manage(*args):
    if args[0] == 'test':
        env.is_test = True
        args = args[1:]

    if not check_basic():
        log.warning('Failed to check(ssh)')
        return

    node = env.node_map.get(env.host)
    filer.mkdir(conf.REMOTE_DIR)
    filer.mkdir(conf.STORAGE_DIR)
    filer.mkdir(conf.TMP_DIR, mode='777')

    db.setuped(1, 'start manage', True)
    for fabscript in node.get('fabruns', []):
        db.create_fabscript(fabscript)
        util.update_log(fabscript, 1, 'start manage')
        db.setuped(1, 'start manage: {0}'.format(fabscript))
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

        util.update_log(fabscript, 0, 'end manage')
        msg = 'end manage: [{0}]'.format(', '.join(msgs))

        db.setuped(status, msg)

    util.dump_node()
