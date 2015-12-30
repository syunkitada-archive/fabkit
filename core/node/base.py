# coding: utf-8

import platform
import getpass
import pickle
import os
import yaml
from fabkit import api, env, util, sudo
from oslo_config import cfg

CONF = cfg.CONF


@api.task
@api.hosts('localhost')
def node(*options):
    len_options = len(options)

    # init env
    env.cmd_history = []  # for debug
    env.last_runs = []
    env.node = {}
    env.node_map = {}
    env.fabscript = {}
    env.fabscript_map = {}
    env.cluster = {}
    env.cluster_map = {}

    if len_options == 0 or options[0] in ['recent', 'r', 'error', 'e']:
        with open(CONF._node_meta_pickle) as f:
            node_meta = pickle.load(f)
        recent_clusters = node_meta['recent_clusters']
        if len(recent_clusters) == 0:
            print 'There are no recent clusters'
            return 0

        if len_options > 1:
            index = int(options[1])
        else:
            index = 0
        cluster = recent_clusters[index]

        cluster_dir = os.path.join(CONF._node_dir, cluster)
        cluster_yaml = os.path.join(cluster_dir, '__cluster.yml')
        cluster_pickle = os.path.join(cluster_dir, '__cluster.pickle')

        node_cluster = None
        if os.path.exists(cluster_pickle):
            with open(cluster_pickle) as f:
                node_cluster = pickle.load(f)
        elif os.path.exists(cluster_yaml):
            with open(cluster_yaml) as f:
                node_cluster = yaml.load(f)
            with open(cluster_pickle, 'w') as f:
                pickle.dump(node_cluster, f)

        if len_options > 0 and options[0] in ['error', 'e']:
            is_only_error = True
        else:
            is_only_error = False

        util.print_cluster(cluster, node_cluster, is_only_error)
        return 0

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
                        sudo('hostname', shell=False)

                util.decode_cluster_map()
                util.dump_status()

            else:
                exit()
