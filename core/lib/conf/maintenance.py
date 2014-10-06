# coding: utf-8

from lib import conf
from lib import util
from fabric.api import env
import os
import commands


def create_required_dirs():
    # create directory, if directory not exists
    def create_dir(directory, is_create_init_py=False):
        if not os.path.exists(directory):
            if util.confirm('"{0}" is not exists. do you want to create?'.format(directory),
                            'Canceled.') or env.is_test:
                os.makedirs(directory)
                print '"{0}" is created.'.format(directory)
                if is_create_init_py:
                    init_py = os.path.join(directory, '__init__.py')
                    with open(init_py, 'w') as f:
                        f.write('# coding: utf-8')
                        print '"{0} is created."'.format(init_py)
            else:
                exit(0)

    create_dir(conf.STORAGE_DIR)
    create_dir(conf.LOG_DIR)
    create_dir(conf.TMP_DIR)
    create_dir(conf.DOWNLOADS_DIR)
    create_dir(conf.NODE_DIR)
    create_dir(conf.FABSCRIPT_MODULE_DIR, True)
    create_dir(conf.FABLIB_MODULE_DIR, True)


def git_clone_required_fablib():
    for fablib_name in conf.CONFIG.options('fablib'):
        fablib = os.path.join(conf.FABLIB_MODULE_DIR, fablib_name)
        git_repo = conf.CONFIG.get('fablib', fablib_name)

        if not os.path.exists(fablib) and not env.is_test:
            cmd_gitclone = 'git clone {0} {1}'.format(git_repo, fablib)
            if util.confirm('{0} is not exists in fablib.\nDo you want to run "{1}"?'.format(fablib_name, cmd_gitclone), 'Canceled.'):  # noqa
                (status, output) = commands.getstatusoutput(cmd_gitclone)
                print output
                if status != 0:
                    exit(0)
            else:
                exit(0)
