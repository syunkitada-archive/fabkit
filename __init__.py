# coding: utf-8

import os
import sys


FABFILE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(FABFILE_DIR, 'core')
WEBAPP_DIR = os.path.join(CORE_DIR, 'webapp')
REPO_DIR = os.path.dirname(FABFILE_DIR)
TEST_REPO_DIR = os.path.join(FABFILE_DIR, 'test/fabrepo')
sys.path.extend([
    WEBAPP_DIR,
    CORE_DIR,
    REPO_DIR,
    TEST_REPO_DIR,
])


# initialize config
from fabkit import conf, util, log
conf.init(FABFILE_DIR, REPO_DIR, TEST_REPO_DIR)
util.create_required_dirs()
util.git_clone_required_fablib()
log.init_logger()


# register fabric tasks
from node import node  # noqa
from setup import setup, manage, check  # noqa
from databag import databag  # noqa
from doc import doc  # noqa
from testtools import test  # noqa


log.set_stdout_pipe()  # 標準出力をパイプ経由でログに流す
