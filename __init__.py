# coding: utf-8

import os
import sys
import subprocess
from fabric.api import env


FABFILE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(FABFILE_DIR, 'core')
REPO_DIR = os.path.dirname(FABFILE_DIR)
TEST_CHEFREPO_DIR = os.path.join(FABFILE_DIR, 'test/chef-repo')
sys.path.extend([
    CORE_DIR,
    REPO_DIR,
])

# initialize config
from lib import conf
conf.init(REPO_DIR, TEST_CHEFREPO_DIR)


# register fabscript task
run = __import__(conf.FABSCRIPT_MODULE, {}, {}, [])
env.last_runs = []
env.host_attrs = {}

# register task
from test import test  # noqa
from node import node, chefnode  # noqa
from cook import cook  # noqa
from check import check  # noqa


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
