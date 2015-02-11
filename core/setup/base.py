# coding: utf-8

from fabkit import env, api, conf, log, filer, status, db, util
import re
from types import DictType
import importlib
import inspect
from check_util import check_basic
from types import IntType, TupleType, StringType


@api.task
def manage(*args):
    if args[0] == 'test':
        option = 'test'
        args = args[1:]
    else:
        option = None

    run_func(args, option)


@api.task
def check(option=None):
    run_func(['^check.*'], option)


@api.task
@api.runs_once
def setup(option=None):
    run_func(['^setup.*', '^check.*'], option)


@api.task
def h(*func_names):
    func_patterns = [re.compile(name) for name in func_names]
    node = env.node_map.get(env.host)
    for fabscript in node.get('fabruns', []):
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

    func_patterns = [re.compile(name) for name in func_names]

    for run in env.runs:
        for cluster_run in run['runs']:
            if len(cluster_run['hosts']) == 0:
                continue

            script_name = cluster_run['name']
            env.cluster = env.cluster_map[run['cluster']]
            cluster_status = env.cluster['__status']
            fabscript_status_map = cluster_status['fabscript_map']
            node_status_map = cluster_status['node_map']
            env.fabscript_map = env.cluster['fabscript_map']
            env.fabscript = env.fabscript_map[script_name]
            env.hosts = cluster_run['hosts']
            # TODO check cluster_run[require]

            script = '.'.join([conf.FABSCRIPT_MODULE, script_name])
            module = importlib.import_module(script)

            module_funcs = []
            for member in inspect.getmembers(module):
                if inspect.isfunction(member[1]):
                    module_funcs.append(member[0])

            for func_pattern in func_patterns:
                for candidate in module_funcs:
                    if func_pattern.match(candidate):
                        func = getattr(module, candidate)
                        if not hasattr(func, 'is_task') or not func.is_task:
                            continue

                        results = api.execute(func)
                        default_result = {
                            'status': 1,
                            'msg': 'Success',
                            'task_status': status.SUCCESS,
                        }
                        for host, tmp_result in results.items():
                            if not tmp_result or type(tmp_result) != DictType:
                                result = default_result
                                results[host] = result
                            else:
                                result = default_result.copy()
                                result.update(tmp_result)
                                results[host] = result

                            node_status_map[host]['fabscript_map'][script_name] = result

                        is_expected = True
                        for host, result in results.items():
                            env
                            if result['task_status'] == status.SUCCESS:
                                result_status = result['status']
                                expected = cluster_run['expected_status']
                                if expected != result_status:
                                    is_expected = False
                                    print '{0}: expected status is {1}, bad status is {2}'.format(
                                        host, expected, result_status)

                            # TODO save database
                            # check continue

                        if is_expected:
                            result = {
                                'status': cluster_run['expected_status'],
                                'task_status': status.SUCCESS,
                            }
                            env.cluster['__status']['fabscript_map'][script_name] = result

                            db.update_all(status.SUCCESS,
                                          status.FABSCRIPT_SUCCESS_MSG.format(script_name))
                        else:
                            print 'For unexpected status is returned, will be exit setup.'
                            exit()
