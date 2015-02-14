# coding: utf-8

import platform
import getpass
from fabkit import api, env, db, util, sudo, status
from django import db as djangodb


@api.task
@api.hosts('localhost')
def node(*options):
    len_options = len(options)

    if len_options == 0 or options[0] in ['recent', 'r', 'error', 'e']:
        return
        length = int(options[1]) if len_options > 1 else None
        if len_options == 0 or options[0] in ['recent', 're']:
            nodes = db.get_recent_nodes(length)
        else:
            nodes = db.get_error_nodes(length)

        for node in nodes:
            util.load_node(node.path)

        util.print_node_map(option='status')

    else:
        query = options[0]
        find_depth = 1
        if len_options > 1:
            option = options[1]
            if option.isdigit():
                find_depth = int(option)

        is_setup = False
        setup_tasks = ['setup', 'manage', 'check']
        for task in env.tasks:
            for setup_task in setup_tasks:
                if task.find(setup_task) == 0:
                    is_setup = True
                    break

        util.load_runs(query, find_depth=find_depth)
        util.print_runs()

        if len(env.tasks) > 1:
            if util.confirm('Are you sure you want to run task on above nodes?', 'Canceled'):
                if is_setup and (not env.password or env.password == ''):
                    print 'Enter your password.\n'
                    if platform.system().find('CYGWIN') == 0:
                        env.password = getpass.getpass()
                    else:
                        sudo('hostname')

                db.update_all(status.REGISTERED, status.REGISTERED_MSG)

                # DBのコネクションを閉じる
                # ここでコネクションを閉じておかないと、次のタスクでIO ERRORが発生してしまう
                djangodb.close_old_connections()
            else:
                exit()
