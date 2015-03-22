# coding: utf-8

import os
import commands
from fabkit import conf, api


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
    for fablib_name in conf.CONFIG.options('fablib'):
        fablib = os.path.join(conf.FABLIB_MODULE_DIR, fablib_name)
        git_repo = conf.CONFIG.get('fablib', fablib_name)

        if not os.path.exists(fablib) and not api.env.is_test:
            cmd_gitclone = 'git clone {0} {1}'.format(git_repo, fablib)
            if util.confirm('{0} is not exists in fablib.\nDo you want to run "{1}"?'.format(fablib_name, cmd_gitclone), 'Canceled.'):  # noqa
                (status, output) = commands.getstatusoutput(cmd_gitclone)
                print output
                if status != 0:
                    exit(0)
            else:
                exit(0)


def create_required_dirs():
    create_dir(conf.STORAGE_DIR)
    create_dir(conf.DATABAG_DIR)
    create_dir(conf.LOG_DIR)
    create_dir(conf.TMP_DIR)
    create_dir(conf.NODE_DIR)
    create_dir(conf.FABSCRIPT_MODULE_DIR, True)
    create_dir(conf.FABLIB_MODULE_DIR, True)
