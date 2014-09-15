# coding: utf-8

import os
import sys
import subprocess
from fabric.api import env


FABFILE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(FABFILE_DIR, 'lib')
REPO_DIR = os.path.dirname(FABFILE_DIR)
TEST_CHEFREPO_DIR = os.path.join(FABFILE_DIR, 'test/chef-repo')
sys.path.extend([
    FABFILE_DIR,
    LIB_DIR,
    REPO_DIR,
])

# initialize config
import conf
# from lib import util
conf.init(REPO_DIR, TEST_CHEFREPO_DIR)


# create directory, if directory not exists
#def create_dir(directory, is_create_init_py=False):
#    if not os.path.exists(directory):
#        if util.confirm('"{0}" is not exists. do you want to create?'.format(directory), 'Canceled.'):
#            os.makedirs(directory)
#            print '"{0}" is created.'.format(directory)
#            if is_create_init_py:
#                init_py = os.path.join(directory, '__init__.py')
#                with open(init_py, 'w') as f:
#                    f.write('# coding: utf-8')
#                    print '"{0} is created."'.format(init_py)
#        else:
#            exit(0)
#
#create_dir(conf.STORAGE_DIR)
#create_dir(conf.LOG_DIR)
#create_dir(conf.PACKAGE_DIR)
#create_dir(conf.FABSCRIPT_MODULE_DIR, True)
#create_dir(conf.FABLIB_MODULE_DIR, True)
#
#for fablib, git_path in conf.FABLIB_MAP.items():
#    if not os.path.exists(fablib):
#        cmd_gitclone = 'git clone {0} {1}'.format(git_path, fablib)
#        if util.confirm('{0} is not exists in fablib.\nDo you want to run "{1}"?'.format(fablib_name, cmd_gitclone), 'Canceled.'):
#            (status, output) = commands.getstatusoutput(cmd_gitclone)
#            print output
#            if status != 0:
#                exit(0)
#        else:
#            exit(0)


# register fabscript task
run = __import__(conf.FABSCRIPT_MODULE, {}, {}, [])
env.last_runs = []

# register task
from fabfile.test import test
from node import node, chefnode
from prepare import prepare
from cook import cook, cookfab
from check import check


from fabric.api import env
len_env_tasks = len(env.tasks)
if len_env_tasks > 0:
    if len_env_tasks == 1 and env.tasks[0].find('node') == 0:
        pass
    else:
        # | tee STDOUT_LOG_FILE
        # Unbuffer output
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

        stdout_log_file = os.path.join(conf.LOG_DIR, conf.STDOUT_LOG_FILE)
        tee = subprocess.Popen(["tee", stdout_log_file], stdin=subprocess.PIPE)
        os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
        os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
