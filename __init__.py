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
# from fabkit import conf, util
from fabkit import util
from fabkit.conf import conf_base, conf_fabric
conf_base.init(FABFILE_DIR, REPO_DIR)
conf_fabric.init()

# conf.init(FABFILE_DIR, REPO_DIR, TEST_REPO_DIR)
# conf.config.init(REPO_DIR, TEST_REPO_DIR)
util.create_required_dirs()
util.git_clone_required_fablib()


# register fabric tasks
from node import node  # noqa
from setup import setup, manage, check  # noqa
from databag import databag  # noqa
from runserver import runserver  # noqa
from doc import doc  # noqa
from testtools import test  # noqa
from util import genconfig  # noqa
