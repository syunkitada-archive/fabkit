import unittest
from node import node
from fabkit import conf, util, env


class TestNode(unittest.TestCase):

    def test_create(self):
        def __test_create(host_pattern, *args):
            conf.init()
            node('create', host_pattern, *args)
            result = sorted([value['path'] for value in env.node_map.values()])
            ex_result = sorted([value[0] for value in util.get_expanded_hosts(host_pattern)])
            self.assertEqual(result, ex_result)

        __test_create('localhost')
        __test_create('test/test[01-03].host')
        __test_create('test/test[01-09].host', 'test.shell')

    def test_edit(self):
        def __test_edit(host_pattern, edit_key, edit_value, result_value):
            conf.init()
            node('edit', host_pattern, edit_key, edit_value)
            for value in env.node_map.values():
                self.assertEqual(value[edit_key], result_value)

        __test_edit('localhost', 'fabruns', 'test.world', ['test.world'])
        __test_edit('test/test0*', 'fabruns', 'test.world', ['test.world'])
        __test_edit('none/test0*', 'fabruns', 'test.world', ['test.world'])

    def test_remove(self):
        def __test_remove(host_pattern):
            conf.init()
            node('remove', host_pattern)
            for host in util.get_expanded_hosts(host_pattern):
                self.assertFalse(util.exists_node(host[0]))

        __test_remove('test0[6-7]*')
        __test_remove('test0[7-9]*')

    def test_node(slef):
        conf.init()
        node()
        node('recent')
        node('error')
