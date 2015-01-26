# coding: utf-8

from fabkit import env, api, conf, log, filer, status, db, util
import re
import importlib
import inspect
from check_util import check_basic
from types import IntType, TupleType, StringType


@api.task
def _manage(*args):
    manage(*args)


@api.task
@api.parallel
def manage(*args):
    if args[0] == 'test':
        option = 'test'
        args = args[1:]
    else:
        option = None

    run_func(args, option)


@api.task
def _check(option=None):
    check(option)


@api.task
@api.parallel
def check(option=None):
    run_func(['^check.*'], option)


@api.task
def _setup(option=None):
    setup(option)


@api.task
@api.parallel
def setup(option=None):
    run_func(['^setup.*', '^check.*'], option)


@api.task
def _help(*func_names):
    func_patterns = [re.compile(name) for name in func_names]
    node = env.node_map.get(env.host)
    for fabscript in node.get('fabruns', []):
        db.create_fabscript(fabscript)
        script = '.'.join((conf.FABSCRIPT_MODULE, fabscript))
        module = importlib.import_module(script)

        module_funcs = []
        for member in inspect.getmembers(module):
            if inspect.isfunction(member[1]):
                if not hasattr(member[1], 'is_task') or not member[1].is_task:
                    continue

                if len(func_patterns) == 0:
                    module_funcs.append(member[0])
                else:
                    for func_pattern in func_patterns:
                        if func_pattern.match(member[0]):
                            module_funcs.append(member[0])
                            help(member[1])

        print module_funcs


def run_func(func_names=[], option=None):
    if option == 'test':
        env.is_test = True

    db.setuped(status.START, status.START_MSG.format(func_names), is_init=True)

    node = env.node_map.get(env.host)
    env.node = node

    if not check_basic():
        db.setuped(status.FAILED_CHECK, 'Failed to check')
        log.warning('Failed to check')
        return

    filer.mkdir(conf.REMOTE_DIR)
    filer.mkdir(conf.REMOTE_STORAGE_DIR)
    filer.mkdir(conf.REMOTE_TMP_DIR, mode='777')

    func_patterns = [re.compile(name) for name in func_names]
    util.load_cluster(node)
    print env.cluster

    for fabscript in node.get('fabruns', []):
        db.create_fabscript(fabscript)
        script = '.'.join((conf.FABSCRIPT_MODULE, fabscript))
        module = importlib.import_module(script)

        module_funcs = []
        for member in inspect.getmembers(module):
            if inspect.isfunction(member[1]):
                module_funcs.append(member[0])

        result_status = None
        for func_pattern in func_patterns:
            for candidate in module_funcs:
                if func_pattern.match(candidate):
                    func = getattr(module, candidate)
                    if not hasattr(func, 'is_task') or not func.is_task:
                        continue

                    db.setuped(status.FABSCRIPT_START,
                               status.FABSCRIPT_START_MSG.format(candidate),
                               fabscript=fabscript)

                    result = func()

                    result_status = None
                    result_msg = None
                    if type(result) is IntType:
                        result_status = result
                    if type(result) is StringType:
                        result_msg = result
                    elif type(result) is TupleType and len(result) == 2 \
                            and type(result[0]) == IntType and type(result[1]) == StringType:
                        result_status, result_msg = result

                    if result_status is None:
                        result_status = status.FABSCRIPT_END
                    if result_msg is None:
                        result_msg = status.FABSCRIPT_END_MSG.format(candidate)

                    db.setuped(result_status, result_msg, fabscript=fabscript)

                    if result_status != 0:
                        log.error('fabscript {0}.{1}: result status is not 0.'.format(fabscript,
                                                                                      candidate))
                        return result_status

        if result_status is None:
            db.setuped(status.FABSCRIPT_END,
                       status.FABSCRIPT_END_EMPTY_MSG,
                       fabscript=fabscript)

    db.setuped(status.END, status.END_MSG.format(func_names))
