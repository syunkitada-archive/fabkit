import unittest
from fabric.api import env
from check import check
import conf

class TestSequenceFunctions(unittest.TestCase):
    def test_check(self):
        conf.init()
        check()
        self.assertEqual([
                    'cmd> ping {0} -c 1 -W 2'.format(env.host),
                    'cmd> ssh {0} hostname'.format(env.host),
                    'run> uptime'
                    ], env.cmd_history)

