import unittest
from node import node, chefnode
import util, conf, testtools


class TestSequenceFunctions(unittest.TestCase):

    def test_create(self):
        def __test_create(host_pattern):
            conf.init()
            node('create', host_pattern)
            for host in util.get_expanded_hosts(host_pattern):
                self.assertEqual(conf.get_initial_json(host), util.load_node_json(host))

        __test_create('localhost')
        __test_create('test[01-09].host')

    def test_edit(self):
        def __test_edit(host_pattern, edit_key, edit_value):
            conf.init()
            node('edit', host_pattern, edit_key, edit_value)
            for host in util.get_available_hosts(host_pattern):
                host_json = util.load_json(host)
                self.assertEqual(edit_value, host_json[edit_key])

        __test_edit('localhost', 'fab_run_list', '[helloworld.hello]')
        __test_edit('test0[6-9]*', 'fab_run_list', '[helloworld.hello]')

    def test_remove(self):
        def __test_remove(host_pattern):
            conf.init()
            node('remove', host_pattern)
            for host in util.get_expanded_hosts(host_pattern):
                self.assertFalse(util.exists_json(host))

        __test_remove('test0[6-7]*')
        __test_remove('test0[7-9]*')
