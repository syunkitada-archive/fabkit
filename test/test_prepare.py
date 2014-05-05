#!/usr/bin/python

import unittest
import conf
from fabric.api import env
from prepare import prepare
from api import *
import test_check

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        env.password = 'test'

    def test_prepare(self):
        conf.init()
        env.cmd_history = []
        prepare('p')
        cmd_history = test_check.get_check_cmds()
        cmd_history.extend([
            'local> scp {0} {1}:{2}'.format(conf.CHEF_RPM, env.host, conf.TMP_CHEF_RPM),
            'sudo> yum install {0} -y'.format(conf.TMP_CHEF_RPM),
            'run> rm -rf {0}'.format(conf.TMP_CHEF_RPM),
            'cmd> rm -f {0}'.format(conf.get_tmp_password_file()),
        ])
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertTrue(env.is_proxy)

        env.cmd_history = []
        prepare()
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)

        env.cmd_history = []
        prepare(None)
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)

    def test_prepare_no_rpm(self):
        conf.CHEF_RPM = '/dev/null/chef.rpm'
        env.cmd_history = []
        prepare()
        self.assertEqual(test_check.get_check_cmds(), env.cmd_history)
        self.assertFalse(env.is_proxy)

        cmd_history = test_check.get_check_cmds()
        cmd_history.extend([
            'local> knife solo prepare {0} --ssh-password {1}'.format(env.host, get_pass(conf.UUID, 'localhost')),
            'cmd> rm -f {0}'.format(conf.get_tmp_password_file('localhost')),
        ])
        conf.CHEF_RPM = ''
        env.cmd_history = []
        prepare()
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)

        conf.CHEF_RPM = None
        env.cmd_history = []
        prepare()
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)


