# coding: utf-8

import unittest
from lib import util
from node import node


class TestUtilHost(unittest.TestCase):
    def test_get_expanded_hosts(self):
        self.assertEqual(
            util.get_expanded_hosts('test[01-03].host'),
            ['test01.host', 'test02.host', 'test03.host'],
        )

        self.assertEqual(
            util.get_expanded_hosts('test[01-03+05].host[1+3-4]'), [
                'test01.host1', 'test01.host3', 'test01.host4',
                'test02.host1', 'test02.host3', 'test02.host4',
                'test03.host1', 'test03.host3', 'test03.host4',
                'test05.host1', 'test05.host3', 'test05.host4'
            ])

        self.assertEqual(util.get_expanded_hosts(1), [])
        self.assertEqual(util.get_expanded_hosts(True), [])
        self.assertEqual(util.get_expanded_hosts(), [])
        self.assertEqual(util.get_expanded_hosts(None), [])

    def test_get_available_hosts(self):
        node('create', 'localhost')
        self.assertEqual(util.get_available_hosts('localhost'),
                         set(['localhost']))

        node('create', 'test0[2+4].host')
        hosts = util.get_available_hosts('test0[2+4]*')
        self.assertEqual(hosts,
                         set(['test02.host', 'test04.host']))

        self.assertEqual(util.get_available_hosts(1), [])
        self.assertEqual(util.get_available_hosts(True), [])
        self.assertEqual(util.get_available_hosts(), [])
        self.assertEqual(util.get_available_hosts(None), [])
