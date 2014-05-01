import unittest
from fabric.api import env
from check import check
import testtools

class TestSequenceFunctions(unittest.TestCase):
    def test_check(self):
        testtools.init_conf()
        check()
        self.assertEqual([
                    'cmd> ping %s -c 1 -W 2' % env.host,
                    'cmd> ssh %s hostname' % env.host,
                    'run> uptime'
                    ], env.cmd_history)

