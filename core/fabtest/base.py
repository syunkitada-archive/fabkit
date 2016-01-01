# coding: utf-8

import os
import re
import sys
import unittest
from fabkit import api, util, env
from oslo_config import cfg
from fabkit.conf import conf_base, conf_fabric, conf_web  # noqa
from node import node  # noqa
from setup import setup  # noqa

CONF = cfg.CONF


@api.task
@api.hosts('localhost')
def test(target=None, t=None, cluster='.*', c=None, fabrun='.*', f=None,
         bootstrap=True, b=None, fablib=None, l=None):
    target = t if t is not None else target
    cluster = c if c is not None else cluster
    re_cluster = re.compile(cluster)
    fabrun = f if f is not None else fabrun
    bootstrap = (not b == 'false') if b is not None else bootstrap
    fablib = l if l is not None else fablib

    sys.path.remove(CONF._repo_dir)

    FABTEST_DIR = os.path.dirname(os.path.abspath(__file__))
    if fablib is not None:
        fablib_dir = os.path.join(CONF._fablib_module_dir, fablib)
        CONF._repo_dir = os.path.join(fablib_dir, 'test-repo')
    else:
        CONF._repo_dir = os.path.join(FABTEST_DIR, 'test-repo')

    EX_CONF = cfg.ConfigOpts()
    conf_file = os.path.join(CONF._repo_dir, 'fabfile.ini')
    if os.path.exists(conf_file):
        EX_CONF([], default_config_files=[conf_file])
    else:
        EX_CONF([])

    from fabkit.conf import conf_base, conf_fabric, conf_web, conf_test  # noqa
    EX_CONF.register_opts(conf_base.default_opts)
    EX_CONF.register_opts(conf_test.test_opts, group="test")

    CONF._storage_dir = os.path.join(CONF._repo_dir, 'storage')
    CONF._databag_dir = os.path.join(CONF._repo_dir, 'databag')
    CONF._tmp_dir = os.path.join(CONF._storage_dir, 'tmp')
    CONF._log_dir = os.path.join(CONF._storage_dir, 'log')
    CONF._node_dir = os.path.join(CONF._repo_dir, 'nodes')
    CONF._node_meta_pickle = os.path.join(CONF._node_dir, 'meta.pickle')
    CONF._fabscript_module_dir = os.path.join(CONF._repo_dir, 'fabscript')
    CONF._fablib_module_dir = os.path.join(CONF._repo_dir, 'fablib')

    CONF.user = CONF.test.user
    CONF.password = CONF.test.password

    sys.path.extend([
        CONF._repo_dir,
    ])

    CONF.fablib = EX_CONF.fablib
    CONF.test.clusters = EX_CONF.test.clusters

    util.create_required_dirs()
    util.git_clone_required_fablib()

    CONF._unittests_dir = os.path.join(FABTEST_DIR, 'unittests')

    if target is None or target == 'fab':
        if bootstrap:
            node('bootstrap/')
            setup()

        env.user = CONF.test.user
        env.password = CONF.test.password
        env.disable_known_hosts = True

        for cluster in CONF.test.clusters:
            if re_cluster.search(cluster):
                node(cluster)
                setup(f=fabrun)

    if fablib is None:
        if target is None:
            suites = unittest.TestLoader().discover(CONF._unittests_dir,
                                                    pattern='test_*')
        else:
            suites = unittest.TestLoader().discover(CONF._unittests_dir,
                                                    pattern='test_{0}*'.format(target))

        alltests = unittest.TestSuite(suites)
        result = unittest.TextTestRunner(verbosity=2).run(alltests)

        exit(len(result.errors) + len(result.failures))
