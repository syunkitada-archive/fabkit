# coding: utf-8

from fabric.api import *  # noqa
import unittest
import commands
from lib import conf


@task
@hosts('localhost')
def test(pattern=None):
    # initialize config for test
    env.is_test = True
    conf.init()

    import os
    DIR = os.path.dirname(__file__)
    # first, remove all node, and create test nodes in test_node
    commands.getoutput('rm -r {0}/*'.format(conf.NODE_DIR))
    if pattern:
        suites = unittest.TestLoader().discover(DIR, pattern='test_{0}*'.format(pattern))
    else:
        suites = unittest.TestLoader().discover(DIR, pattern='test_*')

    alltests = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(alltests)
