import unittest
from node import node
import util, conf

class TestSequenceFunctions(unittest.TestCase):

    def test_node(self):
        conf.init_test_conf()

        node() # for debug

        host_pattern = 'create'
        edit_target = 'localhost'
        node(host_pattern, edit_target)
        for hostname in util.expand_hostname(edit_target):
            self.assertEqual(conf.template_json, util.load_json(hostname))

        edit_target = 'test[01-09].host'
        node(host_pattern, edit_target)
        for hostname in util.expand_hostname(edit_target):
            self.assertEqual(conf.template_json, util.load_json(hostname))

        host_pattern = 'test0[6-9]*'
        edit_target = 'run_list'
        edit_value = 'recipe[test]'
        node(host_pattern, edit_target, edit_value)
        for hostname in util.get_available_hosts(host_pattern):
            host_json = util.load_json(hostname)
            self.assertEqual(edit_value, host_json[edit_target])

        node() # for dubug

        host_pattern = 'remove'
        edit_target = 'test0[6-9]*'
        node(host_pattern, edit_target)
        for hostname in util.get_available_hosts(edit_target):
            self.assertFalse(util.exists_json(hostname))

        node() # for debug


