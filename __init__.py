# coding: utf-8

import os
import sys


FABFILE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(FABFILE_DIR, 'core')
WEBAPP_DIR = os.path.join(CORE_DIR, 'webapp')
REPO_DIR = os.path.dirname(FABFILE_DIR)
sys.path.extend([
    WEBAPP_DIR,
    CORE_DIR,
    REPO_DIR,
])


# initialize config
from fabkit import util
from fabkit.conf import conf_base, conf_fabric, conf_web, conf_test  # noqa
conf_base.init(REPO_DIR)
conf_fabric.init()

util.create_required_dirs()
util.git_clone_required_fablib()


# register fabric tasks
from node import node  # noqa
from setup import setup, manage, check  # noqa
from databag import databag  # noqa
from runserver import runserver  # noqa
from fabtest import test  # noqa
from doc import doc  # noqa
from util import genconfig  # noqa
