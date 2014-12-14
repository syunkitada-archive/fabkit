# coding: utf-8

import unittest
from fabric.api import env

from node import node, chefnode
from setup import setup
from lib import conf
import test_check
import test_node


class TestCook(unittest.TestCase):
    def test_setup(self):
        node('remove', '*')
        env.is_chef = False
        conf.init()

        node('create', 'localhost', 'fabrun_list', 'testscript.test')
        setup()

        cmd_history = test_check.get_check_cmds()
        cmd_history.extend(['run> hostname'])
        self.assertEqual(env.cmd_history, cmd_history)

    def test_setup_for_chef(self):
        host = 'localhost'
        conf.init()
        chefnode(host)
        setup()

        cmd_history = []
        cmd_history.extend(test_node.get_chefnode_cmds(host))
        cmd_history.extend(test_check.get_check_cmds())
        cmd_history.extend(['sudo> chef-client'])
        self.assertEqual(env.cmd_history, cmd_history)
