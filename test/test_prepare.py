#!/usr/bin/python

import unittest
import conf
from fabric.api import *
from prepare import prepare

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        env.password = 'test'

    def test_prepare(self):
        conf.init_test_conf()
        env.cmd_history = []
        prepare('p')
        cmd_history = [
                'local> scp %s %s:~/%s' % (conf.chef_rpm_path, env.host, conf.tmp_chef_rpm),
                'sudo> yum install %s -y' % conf.tmp_chef_rpm,
                'run> rm -rf %s' % conf.tmp_chef_rpm,
                'run> uptime',
                ]
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

        env.cmd_history = []
        prepare(1)
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)

    def test_prepare_no_rpm(self):
        conf.chef_rpm_path = '/dev/null/chef.rpm'
        env.cmd_history = []
        prepare()
        self.assertEqual([], env.cmd_history)
        self.assertFalse(env.is_proxy)

        cmd_history = [
            'local> knife solo prepare %s --ssh-password $PASSWORD' % (env.host),
            'run> uptime',
        ]
        conf.chef_rpm_path = ''
        env.cmd_history = []
        prepare()
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)

        conf.chef_rpm_path = None
        env.cmd_history = []
        prepare()
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)


