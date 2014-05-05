# coding: utf-8

import os, sys

FABFILE_DIR       = os.path.dirname(os.path.abspath(__file__))
LIB_DIR           = os.path.join(FABFILE_DIR, 'lib')
CHEFREPO_DIR      = os.path.dirname(FABFILE_DIR)
TEST_CHEFREPO_DIR = os.path.join(FABFILE_DIR, 'test/chef-repo')
sys.path.extend([
    FABFILE_DIR,
    LIB_DIR,
    CHEFREPO_DIR,
])

# initialize config
import conf
conf.init(CHEFREPO_DIR, TEST_CHEFREPO_DIR)

# register fabscript task
run = __import__(conf.FABSCRIPT_MODULE, {}, {}, [])

# register task
from test import test
from node import node
from role import role
from prepare import prepare
from cook import cook
from check import check

