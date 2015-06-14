# coding: utf-8

import platform
import getpass
import pickle
import os
import yaml
from fabkit import api, env, util, sudo, conf


@api.task
@api.hosts('localhost')
def node(*options):
    len_options = len(options)

    if len_options == 0 or options[0] in ['recent', 'r', 'error', 'e']:
        with open(conf.NODE_META_PICKLE) as f:
            node_meta = pickle.load(f)
        recent_clusters = node_meta['recent_clusters']

        if len(options) > 1:
            index = int(options[1])
        else:
            index = 0
        cluster = recent_clusters[index]

        cluster_dir = os.path.join(conf.NODE_DIR, cluster)
        cluster_yaml = os.path.join(cluster_dir, '__cluster.yml')
        cluster_pickle = os.path.join(cluster_dir, '__cluster.pickle')

        if os.path.exists(cluster_pickle):
            with open(cluster_pickle) as f:
                node_cluster = pickle.load(f)
        elif os.path.exists(cluster_yaml):
            with open(cluster_yaml) as f:
                node_cluster = yaml.load(f)
            with open(cluster_pickle, 'w') as f:
                pickle.dump(node_cluster, f)

        if options[0] in ['error', 'e']:
            is_only_error = True
        else:
            is_only_error = False

        util.print_cluster(cluster, node_cluster, is_only_error)
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
            elif task.find('datamap') == 0:
                env.is_datamap = True

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
