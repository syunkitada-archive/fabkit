# coding: utf-8

import os
import unittest
from fabkit import api, util
from oslo_config import cfg
from fabkit.conf import conf_base, conf_fabric, conf_web  # noqa

CONF = cfg.CONF


@api.task
@api.hosts('localhost')
def test(pattern=None):
    FABTEST_DIR = os.path.dirname(os.path.abspath(__file__))
    CONF._repo_dir = os.path.join(FABTEST_DIR, 'test-repo')
    CONF._storage_dir = os.path.join(CONF._repo_dir, 'storage')
    CONF._databag_dir = os.path.join(CONF._repo_dir, 'databag')
    CONF._tmp_dir = os.path.join(CONF._storage_dir, 'tmp')
    CONF._log_dir = os.path.join(CONF._storage_dir, 'log')
    CONF._node_dir = os.path.join(CONF._repo_dir, 'nodes')
    CONF._fabscript_module_dir = os.path.join(CONF._repo_dir, 'fabscript')
    CONF._fablib_module_dir = os.path.join(CONF._repo_dir, 'fablib')
    CONF._node_meta_pickle = os.path.join(CONF._node_dir, 'meta.pickle')
    CONF.fablib = {}

    util.create_required_dirs()
    util.git_clone_required_fablib()

    CONF._unittests_dir = os.path.join(FABTEST_DIR, 'unittests')

    if pattern is None:
        suites = unittest.TestLoader().discover(CONF._unittests_dir,
                                                pattern='test_*')
    else:
        suites = unittest.TestLoader().discover(CONF._unittests_dir,
                                                pattern='test_{0}*'.format(pattern))
    alltests = unittest.TestSuite(suites)
    result = unittest.TextTestRunner(verbosity=2).run(alltests)

    exit(len(result.errors) + len(result.failures))
