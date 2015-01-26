import unittest
from fabkit import env, util, conf
from node import node
import os


class TestUtilNode(unittest.TestCase):

    def test_get_node_file(self):
        util.get_node_file('localhost')
        result = os.path.join(conf.NODE_DIR, '{0}.yaml'.format('localhost'))
        self.assertEqual(util.get_node_file('localhost'), result)

    def test_exists_node(self):
        node('create', 'localhost')
        self.assertTrue(util.exists_node('localhost'))
        self.assertFalse(util.exists_node('nonehost'))

    def test_dump_load_node(self):
        host = 'localhost'
        conf.init()

        util.dump_node(host, is_init=True)
        tmp_node = util.convert_node()
        tmp_node.update({'path': host})
        self.assertEqual(util.load_node(host), tmp_node)
        self.assertTrue(host in env.hosts)
        self.assertTrue(host in env.node_map)

        util.remove_node('localhost')
        self.assertTrue(len(util.get_available_hosts('localhost')) == 0)
        util.print_node_map()

    def test_load_node_map(self):
        host = 'localhost[1-3]'
        node('create', host)
        conf.init()

        util.load_node_map(host)
        util.print_node_map()

        self.assertEqual(sorted(util.get_expanded_hosts(host)), sorted(env.hosts))
        for host, result_node in env.node_map.items():
            self.assertTrue(host in util.get_expanded_hosts(host))
