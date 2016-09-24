# coding: utf-8

from fabkit import env, api, log, cmd, container
from oslo_config import cfg
from setup import setup

CONF = cfg.CONF


@api.task
def job(*args, **kwargs):
    runs = env.runs
    for run in runs:
        cluster_name = run['cluster']
        cluster = env.cluster_map[cluster_name]
        job = cluster.get('job', {})
        pipelines = job.get('pipelines', [])
        if len(args) == 0:
            return

        if args[0] == 'start':
            print 'start'
        elif args[0] == 'status':
            print 'status'
        elif args[0] == 'stop':
            print 'stop'
        elif args[0] == 'local':
            for pipeline in pipelines:
                if len(args) == 1 or args[1] == pipeline['name']:
                    exec_pipelines(cluster, run, pipeline['runs'])


def exec_pipelines(cluster, run, pipelines):
    status = 0
    if_statement = False
    for pipeline in pipelines:
        if isinstance(pipeline, str):
            exec_command(cluster, run, pipeline)
        elif isinstance(pipeline, dict):
            for key, value in pipeline.items():
                splited_key = key.split(' ', 1)
                if splited_key[0] == 'if':
                    if_statement = True
                    if eval(splited_key[1]):
                        if_statement = False
                        exec_pipelines(cluster, run, value)
                elif if_statement == splited_key[0] == 'elif':
                    if eval(splited_key[1]):
                        if_statement = False
                        exec_pipelines(cluster, run, value)
                elif if_statement == splited_key[0] == 'else':
                    if_statement = False
                    exec_pipelines(cluster, run, value)

    return status


def exec_command(cluster, run, command):
    log.info('exec_command: {0}'.format(command))
    action = command.split(' ', 1)
    result = 0
    if action[0] == 'sh':
        result = cmd(action[1])[0]
    elif action[0] == 'create':
        env.is_local = True
        env.host = 'localhost'
        container.create(cluster[action[1]])
        env.is_local = False
    elif action[0] == 'delete':
        env.is_local = True
        env.host = 'localhost'
        container.delete(cluster[action[1]])
        env.is_local = False
    elif action[0] == 'setup':
        env.runs = [run]
        env.user = CONF.job_user
        env.password = CONF.job_password
        CONF.user = CONF.job_user
        CONF.password = CONF.job_password
        setup()

    log.info('result_command: {0}({1})'.format(command, result))
    return result
