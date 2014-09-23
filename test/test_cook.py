import unittest
from cook import cook
from fabric.api import env
from lib import conf
from lib import util
import test_check


class TestSequenceFunctions(unittest.TestCase):
    def test_cook(self):
        conf.init()
        env.is_chef = False
        host_json = util.load_json()
        host_json['fab_run_list'] = ['testscript.test']
        util.dump_json(host_json)

        cook()
        cmd_history = test_check.get_check_cmds()
        cmd_history.extend(['run> hostname'])
        self.assertEqual(cmd_history, env.cmd_history)

    def test_cook_for_chef(self):
        conf.init()
        env.is_chef = True
        cook()
        cmd_history = test_check.get_check_cmds()
        cmd_history.extend(['sudo> chef-client'])
        self.assertEqual(cmd_history, env.cmd_history)
