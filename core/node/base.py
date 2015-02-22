# coding: utf-8

import platform
import getpass
from fabkit import api, env, util, sudo


@api.task
@api.hosts('localhost')
def node(*options):
    len_options = len(options)

    if len_options == 0 or options[0] in ['recent', 'r', 'error', 'e']:
        # TODO print recent result and error result
        return

    else:
        query = options[0]
        find_depth = 1
        is_yes = False
        if len_options > 1:
            option = options[1]
            if option.isdigit():
                find_depth = int(option)
            elif option == 'yes':
                is_yes = True

        for task in env.tasks:
            if task.find('setup') == 0:
                env.is_setup = True
            elif task.find('check') == 0:
                env.is_check = True
            elif task.find('manage') == 0:
                env.is_manage = True

        util.load_runs(query, find_depth=find_depth)
        util.print_runs()

        if len(env.tasks) > 1:
            if is_yes or util.confirm(
                    'Are you sure you want to run task on above nodes?', 'Canceled'):
                if (env.is_setup or env.is_check or env.is_manage) \
                        and (not env.password or env.password == ''):
                    print 'Enter your password.\n'
                    if platform.system().find('CYGWIN') == 0:
                        env.password = getpass.getpass()
                    else:
                        sudo('hostname')

                util.decode_cluster_map()
                util.dump_status()

            else:
                exit()
