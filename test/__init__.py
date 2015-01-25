# coding: utf-8

import os
import unittest
import commands
from fabkit import conf, api, env


@api.task
@api.hosts('localhost')
def test(pattern=None):
    # initialize config for test
    env.is_test = True
    conf.init()

    DIR = os.path.dirname(__file__)
    print conf.TEST_REPO_DIR

    return
    # first, remove all node, and create test nodes in test_node
    commands.getoutput('rm -r {0}/*'.format(conf.NODE_DIR))
    if pattern:
        suites = unittest.TestLoader().discover(DIR, pattern='test_{0}*'.format(pattern))
    else:
        suites = unittest.TestLoader().discover(DIR, pattern='test_*')

    alltests = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(alltests)
