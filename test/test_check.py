import unittest
from fabric.api import env
from check import check
import conf

class TestSequenceFunctions(unittest.TestCase):
    def test_check(self):
        conf.init()
        check()
        self.assertEqual(get_check_cmds(), env.cmd_history)

def get_check_cmds():
    return [
            'cmd> ping {0} -c 1 -W 2'.format(env.host),
            'cmd> ssh {0} hostname'.format(env.host),
            'run> uptime',
            ]

