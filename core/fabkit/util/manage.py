# coding: utf-8

import os
import commands
from fabkit import conf, api
import pickle
import ConfigParser


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

    for fablib_name in conf.CONFIG.options('fablib'):
        git_repo = conf.CONFIG.get('fablib', fablib_name)
        git_clone(fablib_name, git_repo)


def git_clone(fablib_name, git_repo):
    fablib = os.path.join(conf.FABLIB_MODULE_DIR, fablib_name)
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
    create_dir(conf.STORAGE_DIR)
    create_dir(conf.DATABAG_DIR)
    create_dir(conf.LOG_DIR)
    create_dir(conf.TMP_DIR)
    create_dir(conf.NODE_DIR)
    create_dir(conf.FABSCRIPT_MODULE_DIR, True)
    create_dir(conf.FABLIB_MODULE_DIR, True)

    if not os.path.exists(conf.NODE_META_PICKLE):
        node_meta = {
            'recent_clusters': [],
        }

        with open(conf.NODE_META_PICKLE, 'w') as f:
            pickle.dump(node_meta, f)
