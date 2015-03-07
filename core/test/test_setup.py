# coding: utf-8

import unittest
from node import node
from setup import _manage, manage, _check, check, _setup, setup
from fabkit import conf, env


class TestSetup(unittest.TestCase):
    def test_setup(self):
        conf.init()
        node('create', 'localhost', 'test.shell')
        setup()
        check()
        manage('restart')

        self.assertTrue('run> date > /etc/motd' in env.cmd_history)
        self.assertTrue('run> date >> /etc/motd' in env.cmd_history)
        self.assertTrue('sudo> service crond status' in env.cmd_history)
        self.assertTrue('sudo> service crond restart' in env.cmd_history)

    def test_serial_setup(self):
        conf.init()
        node('create', 'localhost', 'test.shell')
        _setup()
        _check()
        _manage('restart')

        self.assertTrue('run> date > /etc/motd' in env.cmd_history)
        self.assertTrue('run> date >> /etc/motd' in env.cmd_history)
        self.assertTrue('sudo> service crond status' in env.cmd_history)
        self.assertTrue('sudo> service crond restart' in env.cmd_history)
