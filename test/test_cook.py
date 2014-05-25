import unittest
from cook import fabcook, cook
from fabric.api import env
import conf, testtools, util
import json
import test_check

class TestSequenceFunctions(unittest.TestCase):
    def test_fabcook(self):
        conf.init()
        host_json = util.load_json()
        host_json['fab_run_list'] = ['testscript.test']
        util.dump_json(host_json)

        fabcook()
        cmd_history = test_check.get_check_cmds()
        cmd_history.extend(['run> hostname'])
        self.assertEqual(cmd_history, env.cmd_history)

    def test_cook(self):
        conf.init()
        cook('p')
        cmd_history = test_check.get_check_cmds()
        cmd_history.extend([
                    'run> rm -rf chef-solo',
                    'local> scp -o "StrictHostKeyChecking=no" ~/chef-solo.tar.gz {0}:~/'.format(env.host),
                    'run> tar -xvf chef-solo.tar.gz',
                    'run> rm -f chef-solo.tar.gz',
                    'run> echo \'{0}\' > chef-solo/solo.json'.format(conf.get_jsonstr_for_chefsolo()),
                    'sudo> chef-solo -c chef-solo/solo.rb -j chef-solo/solo.json',
                ])
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertTrue(env.is_proxy)

        env.cmd_history = []
        cook()
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)
