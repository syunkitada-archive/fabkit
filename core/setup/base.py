# coding: utf-8

from fabkit import env, api, conf, status, log, util
import re
from types import DictType
import inspect
from remote import run_remote


@api.task
def manage(*args, **kwargs):
    run_func(args, *args, **kwargs)


@api.task
def check(*args, **kwargs):
    run_func(['^check.*'], *args, **kwargs)


@api.task
@api.runs_once
def setup(*args, **kwargs):
    run_func(['^setup.*'], *args, **kwargs)


def run_func(func_names=[], *args, **kwargs):
    fabrun_filter = []
    is_filter = False
    env.is_test = False
    env.is_help = False
    env.is_remote = False
    if len(args) > 0:
        if args[0] == 'test':
            env.is_test = True
            args = args[1:]
        elif args[0] == 'help':
            env.is_help = True
            args = args[1:]
        elif args[0] == 'remote':
            env.is_remote = True
            args = args[1:]
    if 'f' in kwargs:
        fabrun_filter = kwargs['f'].split('+')
        fabrun_filter = [re.compile(f) for f in fabrun_filter]
        is_filter = True

    env.is_remote = False
    if env.is_remote:
        env.remote_map = {}
        remote_hosts = set()
        tmp_runs = []
        for i, run in enumerate(env.runs):
            cluster = env.cluster_map[run['cluster']]
            if 'remote' in cluster:
                cluster = env.cluster_map[run['cluster']]
                if 'remote' in cluster:
                    cluster_remote = cluster['remote']
                    remote = env.remote_map.get(cluster_remote['host'], {
                        'clusters': [],
                        'host_pattern': cluster['host_pattern'],
                    })
                    env.remote_map[cluster_remote['host']] = remote

                    remote['clusters'].append(cluster['name'])
                    remote_hosts.add(cluster_remote['host'])
            else:
                tmp_runs.append(run)

        env.runs = tmp_runs
        if len(remote_hosts) > 0:
            env.func_names = func_names
            env.hosts = list(remote_hosts)
            results = api.execute(run_remote)
            for host, result in results.items():
                env.cluster_map.update(result)

            util.dump_status()

    func_patterns = [re.compile(name) for name in func_names]
    host_filter = {}
    for run in env.runs:
        log.init_logger(run['cluster'])
        for cluster_run in run['runs']:
            run_results = []
            script_name = cluster_run['fabscript']

            if is_filter:
                for f in fabrun_filter:
                    if f.search(script_name):
                        break
                else:
                    continue

            if env.is_check or env.is_manage:
                # 二重実行を防ぐ
                hosts = host_filter.get(script_name, [])
                tmp_hosts = list(set(cluster_run['hosts']) - set(hosts))
                cluster_run['hosts'] = tmp_hosts
                hosts.extend(tmp_hosts)
                host_filter[script_name] = hosts

            if len(cluster_run['hosts']) == 0:
                continue

            hosts = []
            for host in cluster_run['hosts']:
                env.node_map[host] = env.node_map.get(host, {
                    'bootstrap_status': -1,
                })
                if env.node_map[host]['bootstrap_status'] != status.FAILED_CHECK:
                    hosts.append(host)

            env.script_name = script_name
            env.hosts = hosts
            env.cluster = env.cluster_map[run['cluster']]

            # override env
            if 'env' in env.cluster:
                cluster_env = env.cluster['env']
                for key, value in cluster_env.items():
                    setattr(env, key, value)

            env.cluster_status = env.cluster['__status']
            env.node_status_map = env.cluster_status['node_map']
            env.fabscript_status_map = env.cluster_status['fabscript_map']
            env.fabscript = env.fabscript_status_map[script_name]

            log.info('hosts: {0}'.format(env.hosts))
            log.info('run: {0}: {1}'.format(script_name, env.fabscript))
            log.debug('node_status_map: {0}'.format(env.node_status_map))

            # check require
            require = env.cluster['fabscript_map'][script_name]['require']
            if env.is_setup:
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

            script = '.'.join([conf.FABSCRIPT_MODULE, script_name.replace('/', '.')])

            # importlibは、2.7以上じゃないと使えない
            # module = importlib.import_module(script)
            module = __import__(script, globals(), locals(), ['*'], -1)

            module_funcs = []
            for member in inspect.getmembers(module):
                if inspect.isfunction(member[1]):
                    module_funcs.append(member[0])

            if env.is_help and len(func_patterns) == 0:
                for candidate in module_funcs:
                    func = getattr(module, candidate)
                    print 'Task: {0}'.format(func.__name__)
                    print func.__doc__
                continue

            # func_patterns にマッチしたタスク関数をすべて実行する
            is_expected = False
            is_contain_unexpected = False
            for func_pattern in func_patterns:
                for candidate in module_funcs:
                    if not func_pattern.match(candidate):
                        continue

                    func = getattr(module, candidate)

                    if not hasattr(func, 'is_task') or not func.is_task:
                        continue

                    # taskデコレータの付いているものだけ実行する
                    if env.is_help:
                        print 'Task: {0}'.format(func.__name__)
                        print func.__doc__
                        continue

                    results = api.execute(func, *args, **kwargs)

                    # check results
                    data_map = {}
                    tmp_status = None
                    is_contain_failed = False
                    for host, result in results.items():
                        env.node_map[host].update(result['node'])
                        if not result or type(result) is not DictType:
                            result = {}

                        node_result = env.node_status_map[host]['fabscript_map'][script_name]
                        result_status = result.get('status')
                        task_status = result.get('task_status', status.SUCCESS)
                        msg = result.get('msg')
                        if msg is None:
                            if task_status is status.SUCCESS:
                                msg = status.FABSCRIPT_SUCCESS_MSG
                            else:
                                msg = status.FABSCRIPT_FAILED_MSG

                        if func.is_bootstrap:
                            if task_status == status.FAILED_CHECK or \
                                    task_status == status.FAILED_CHECK_PING:
                                env.node_map[host]['bootstrap_status'] = status.FAILED_CHECK
                            else:
                                env.node_map[host]['bootstrap_status'] = status.SUCCESS

                        node_result['task_status'] = task_status

                        tmp_data_map = result.get('data_map')
                        if tmp_data_map is not None:
                            for map_name, tmp_map_data in tmp_data_map.items():
                                if tmp_map_data['type'] == 'table':
                                    map_data = data_map.get(map_name, {
                                        'name': map_name,
                                        'type': 'table',
                                        'data': [],
                                    })

                                    tmp_data = {'!!host': host}
                                    tmp_data.update(tmp_map_data['data'])
                                    map_data['data'].append(tmp_data)
                                    data_map[map_name] = map_data

                        if env.is_setup:
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
                                    log.error('expected status is {0}, bad status is {1}.'.format(  # noqa
                                        expected, result_status), host)

                        elif env.is_check:
                            node_result['check_msg'] = msg
                            if result_status is None:
                                result_status = status.SUCCESS

                            node_result.update({
                                'check_status': result_status,
                            })
                            if result_status != status.SUCCESS:
                                log.error('Failed check {0}.{1} [{2}]. {3}'.format(  # noqa
                                    script_name, candidate, result_status, msg), host)

                        if task_status == status.SUCCESS:
                            log.info('Success task {0}.{1} [{2}]. {3}'.format(
                                script_name, candidate, task_status, msg), host)
                        else:
                            log.error('Failed task {0}.{1} [{2}]. {3}'.format(
                                script_name, candidate, task_status, msg), host)
                            is_contain_failed = True

                    # end for host, result in results.items():

                    if len(data_map) > 0:
                        util.dump_datamap(data_map)

                    if is_contain_failed:
                        log.error('Failed task {0}.{1}. Exit setup.'.format(
                            script_name, candidate))
                        util.dump_status()
                        exit()

                    if tmp_status is not None:
                        env.fabscript['tmp_status'] = tmp_status

                # for candidate in module_funcs:
            # for func_pattern in func_patterns:

            if env.is_setup:
                if is_expected and not is_contain_unexpected or cluster_run['expected_status'] == 0:
                    env.cluster['__status']['fabscript_map'][script_name] = {
                        'status': cluster_run['expected_status'],
                        'task_status': status.SUCCESS,
                    }

                    util.dump_status()
                else:
                    log.error('bad status.')
                    exit()
            elif env.is_check:
                env.cluster['__status']['fabscript_map'][script_name]['task_status'] = status.SUCCESS   # noqa
                util.dump_status()
            elif env.is_manage:
                env.cluster['__status']['fabscript_map'][script_name]['task_status'] = status.SUCCESS   # noqa
                util.dump_status()

        # end for cluster_run in run['runs']:
    # end for run in env.runs:
