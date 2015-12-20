# coding: utf-8

import os
import commands
from fabkit import api
from oslo_config import cfg
import pickle
import ConfigParser

CONF = cfg.CONF


# create directory, if directory not exists
def create_dir(directory, is_create_init_py=False):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print '"{0}" is created.'.format(directory)
        if is_create_init_py:
            init_py = os.path.join(directory, '__init__.py')
            with open(init_py, 'w') as f:
                f.write('# coding: utf-8')
                print '"{0} is created."'.format(init_py)


def git_clone_required_fablib():
    if api.env.is_test:
        return

    for fablib_name, git_repo in CONF.fablib.items():
        git_clone(fablib_name, git_repo)


def git_clone(fablib_name, git_repo):
    fablib = os.path.join(CONF._fablib_module_dir, fablib_name)
    if not os.path.exists(fablib):
        cmd_gitclone = 'git clone {0} {1}'.format(git_repo, fablib)
        print cmd_gitclone
        (status, output) = commands.getstatusoutput(cmd_gitclone)
        print output
        if status != 0:
            exit(0)

    if os.path.exists(fablib):
        config = ConfigParser.SafeConfigParser()
        fablib_ini = os.path.join(fablib, 'fablib.ini')
        if os.path.exists(fablib_ini):
            config.read(fablib_ini)
            for require_fablib_name in config.options('fablib'):
                git_repo = config.get('fablib', require_fablib_name)
                git_clone(require_fablib_name, git_repo)


def create_required_dirs():
    create_dir(CONF._storage_dir)
    create_dir(CONF._databag_dir)
    create_dir(CONF._tmp_dir)
    # create_dir(conf.LOG_DIR)
    create_dir(CONF._node_dir)
    create_dir(CONF._fabscript_module_dir, True)
    create_dir(CONF._fablib_module_dir, True)

    if not os.path.exists(CONF._node_meta_pickle):
        node_meta = {
            'recent_clusters': [],
        }

        with open(CONF._node_meta_pickle, 'w') as f:
            pickle.dump(node_meta, f)
