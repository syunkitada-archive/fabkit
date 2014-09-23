# coding: utf-8

from fabric.api import *  # noqa
import unittest
import commands
from lib import conf
import test_util
import test_cook
import test_node
import test_check


@task
@hosts('localhost')
def test():
    # initialize config for test
    env.is_test = True
    conf.init()

    # first, remove all node, and create test nodes in test_node
    commands.getoutput('rm -r {0}/*'.format(conf.NODE_DIR))
    suites = [
        unittest.TestLoader().loadTestsFromTestCase(test_node.TestSequenceFunctions),
        unittest.TestLoader().loadTestsFromTestCase(test_util.TestSequenceFunctions),
        unittest.TestLoader().loadTestsFromTestCase(test_check.TestSequenceFunctions),
        unittest.TestLoader().loadTestsFromTestCase(test_cook.TestSequenceFunctions),
    ]

    alltests = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=2).run(alltests)
