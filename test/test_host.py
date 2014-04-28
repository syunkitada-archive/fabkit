# coding: utf-8

import unittest
from host import host
from fabric.api import env
import conf

class TestSequenceFunctions(unittest.TestCase):
    def test_host(self):
        conf.init_test_conf()
        host('test0[2+4]*')
        self.assertEqual(
                env.hosts,
                set(['test02.host', 'test04.host'])
            )

        host()
        self.assertEqual(env.hosts, [])

        host(None)
        self.assertEqual(env.hosts, [])
