# coding: utf-8

from fabkit import env, api, conf, status, log, util
import re
from types import DictType
import importlib
import inspect


@api.task
def manage(*args):
    if len(args) > 0 and args[0] == 'test':
        option = 'test'
        args = args[1:]
    else:
        option = None

    run_func(args, option, is_manage=True)


@api.task
def check(option=None):
    run_func(['^check.*'], option, is_check=True)


@api.task
@api.runs_once
def setup(option=None):
    run_func(['^setup.*'], option, is_setup=True)


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


def run_func(func_names=[], option=None, is_setup=False, is_check=False, is_manage=False):
    if option == 'test':
        env.is_test = True

    func_patterns = [re.compile(name) for name in func_names]
    host_filter = {}
    for run in env.runs:
        for cluster_run in run['runs']:
            script_name = cluster_run['fabscript']

            if is_check or is_manage:
                # 二重実行を防ぐ
                hosts = host_filter.get(script_name, [])
                tmp_hosts = list(set(cluster_run['hosts']) - set(hosts))
                cluster_run['hosts'] = tmp_hosts
                hosts.extend(tmp_hosts)
                host_filter[script_name] = hosts

            if len(cluster_run['hosts']) == 0:
                continue

            env.script_name = script_name
            env.hosts = cluster_run['hosts']
            env.cluster = env.cluster_map[run['cluster']]
            env.cluster_status = env.cluster['__status']
            env.node_status_map = env.cluster_status['node_map']
            env.fabscript_status_map = env.cluster_status['fabscript_map']
            env.fabscript = env.fabscript_status_map[script_name]

            log.info('run: {0}'.format(script_name))
            log.info('status: {0}'.format(env.fabscript))
            log.info('hosts: {0}'.format(env.hosts))
            log.debug('node_status_map: {0}'.format(env.node_status_map))

            # check require
            require = env.cluster['fabscript_map'][script_name]['require']
            if is_setup:
                is_require = True
                for script, status_code in require.items():
                    required_status = env.fabscript_status_map[script]['status']
                    if required_status != status_code:
                        log.error('Require Error\n'
                                  + '{0} is require {1}:{2}.\nbut {1} status is {3}.'.format(
                                      script_name, script, status_code, required_status))
                        is_require = False
                        break
                if not is_require:
                    break

            # print cluster_run[require]

            script = '.'.join([conf.FABSCRIPT_MODULE, script_name])
            module = importlib.import_module(script)

            module_funcs = []
            for member in inspect.getmembers(module):
                if inspect.isfunction(member[1]):
                    module_funcs.append(member[0])

            # func_patterns にマッチしたタスク関数をすべて実行する
            is_expected = False
            is_contain_unexpected = False
            for func_pattern in func_patterns:
                for candidate in module_funcs:
                    if func_pattern.match(candidate):
                        # taskデコレータの付いているものだけ実行する
                        func = getattr(module, candidate)
                        if not hasattr(func, 'is_task') or not func.is_task:
                            continue
                        results = api.execute(func)

                        # check results
                        tmp_status = None
                        is_contain_failed = False
                        for host, result in results.items():
                            if not result or type(result) is not DictType:
                                result = {}

                            node_result = env.node_status_map[host]['fabscript_map'][script_name]
                            result_status = result.get('status')
                            task_status = result.get('task_status', status.SUCCESS)
                            msg = result.get('msg',
                                             status.FABSCRIPT_SUCCESS_MSG.format(candidate))

                            node_result['task_status'] = task_status

                            if is_setup:
                                node_result['msg'] = msg
                                if result_status is not None:
                                    tmp_status = result_status
                                    node_result['status'] = result_status
                                    expected = cluster_run['expected_status']
                                    if expected == result_status:
                                        is_expected = True
                                        log.info('{0}: {1} is expected status.'.format(
                                            host, msg, result_status))
                                    else:
                                        is_contain_unexpected = True
                                        log.error('{0}: expected status is {1}, bad status is {2}.'.format(  # noqa
                                            host, expected, result_status))
                            elif is_check:
                                node_result['check_msg'] = msg
                                if result_status is None:
                                    result_status = status.SUCCESS

                                node_result.update({
                                    'check_status': result_status,
                                })
                                if result_status != status.SUCCESS:
                                    log.error('{0}: failed check {1}.{2} [{3}]. {4}'.format(  # noqa
                                        host, script_name, candidate, result_status, msg))

                            if task_status != status.SUCCESS:
                                log.error('{0}: Failed task {1}.{2} [{3}]. {4}'.format(
                                    host, script_name, candidate, task_status, msg))
                                is_contain_failed = True

                        if is_contain_failed:
                            log.error('Failed task {0}.{1}. Exit setup.'.format(
                                script_name, candidate))
                            util.dump_status()
                            exit()

                        if tmp_status is not None:
                            env.fabscript['tmp_status'] = tmp_status

            if is_setup:
                if is_expected and not is_contain_unexpected or cluster_run['expected_status'] == 0:
                    env.cluster['__status']['fabscript_map'][script_name] = {
                        'status': cluster_run['expected_status'],
                        'task_status': status.SUCCESS,
                    }

                    util.dump_status()
                else:
                    log.error('bad status.')
                    exit()
            elif is_check:
                env.cluster['__status']['fabscript_map'][script_name]['task_status'] = status.SUCCESS   # noqa
                util.dump_status()
