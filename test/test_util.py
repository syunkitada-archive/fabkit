# coding: utf-8

import unittest
import util, conf
import re

class TestSequenceFunctions(unittest.TestCase):
    def test_get_expanded_hosts(self):
        self.assertEqual(
                util.get_expanded_hosts('test[01-03].host'),
                [ 'test01.host', 'test02.host', 'test03.host' ]
            )

        self.assertEqual(
                util.get_expanded_hosts('test[01-03+05].host[1+3-4]'),
                [ 'test01.host1', 'test01.host3', 'test01.host4',
                  'test02.host1', 'test02.host3', 'test02.host4',
                  'test03.host1', 'test03.host3', 'test03.host4',
                  'test05.host1', 'test05.host3', 'test05.host4']
            )

        self.assertEqual(util.get_expanded_hosts(1), [])
        self.assertEqual(util.get_expanded_hosts(True), [])
        self.assertEqual(util.get_expanded_hosts(), [])
        self.assertEqual(util.get_expanded_hosts(None), [])

    def test_get_available_hosts(self):
        self.assertEqual(
                util.get_available_hosts('localhost'),
                set(['localhost'])
            )

        self.assertEqual(
                util.get_available_hosts('test0[2+4]*'),
                set(['test02.host', 'test04.host'])
            )

        self.assertEqual(util.get_available_hosts(1), [])
        self.assertEqual(util.get_available_hosts(True), [])
        self.assertEqual(util.get_available_hosts(), [])
        self.assertEqual(util.get_available_hosts(None), [])

    def test_json(self):
        host = 'test99.host'
        util.dump_json(conf.get_initial_json(host), host)
        self.assertTrue(util.exists_json(host))
        self.assertEqual(conf.get_initial_json(host), util.load_json(host))
        util.remove_json(host)
        self.assertFalse(util.exists_json(host))

    def test_get_timestamp(self):
        prog = re.compile('[1-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-2][0-9]:[0-6][0-9]:[0-6][0-9]')
        self.assertTrue(prog.match(util.get_timestamp()))

    def test_confirm(self):
        self.assertTrue(util.confirm('Is ok?'))
        self.assertTrue(util.confirm('Is ok?', 'Canceled'))
