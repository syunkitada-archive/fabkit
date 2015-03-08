# coding: utf-8

import os
import unittest
import commands
from fabkit import conf, api, env, util


@api.task
@api.hosts('localhost')
def test(pattern=None):
    # initialize config for test
    env.is_test = True
    conf.init()
    util.create_required_dirs()
    commands.getoutput('rm -rf {0}/*'.format(conf.NODE_DIR))
    commands.getoutput('rm -rf {0}/*'.format(conf.TMP_DIR))
    commands.getoutput('rm -rf {0}/*'.format(conf.LOG_DIR))

    DIR = os.path.dirname(__file__)

    # first, remove all node, and create test nodes in test_node
    if pattern:
        suites = unittest.TestLoader().discover(DIR, pattern='test_{0}*'.format(pattern))
    else:
        suites = unittest.TestLoader().discover(DIR, pattern='test_*')

    alltests = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(alltests)
