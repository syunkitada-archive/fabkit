import unittest
from cook import cook
from fabric.api import env
import conf, testtools
import json

class TestSequenceFunctions(unittest.TestCase):
    def test_cook(self):
        conf.init()
        cook('p')
        cmd_history = [
                    'run> rm -rf chef-solo',
                    'local> scp ~/chef-solo.tar.gz {0}:~/'.format(env.host),
                    'run> tar -xvf chef-solo.tar.gz',
                    'run> rm -f chef-solo.tar.gz',
                    'run> echo \'{0}\' > chef-solo/solo.json'.format(conf.get_jsonstr_for_chefsolo()),
                    'sudo> chef-solo -c chef-solo/solo.rb -j chef-solo/solo.json',
                    'run> uptime',
                ]
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertTrue(env.is_proxy)

        env.cmd_history = []
        cook()
        self.assertEqual(cmd_history, env.cmd_history)
        self.assertFalse(env.is_proxy)
