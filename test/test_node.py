import unittest
from fabric.api import env
from node import node, nodesolo
import util, conf, testtools

class TestSequenceFunctions(unittest.TestCase):

    def test_create(self):
        def __test_create(host_pattern):
            conf.init()
            nodesolo('create', host_pattern)
            for host in util.get_expanded_hosts(host_pattern):
                self.assertEqual(conf.get_initial_json(host), util.load_node_json(host))

        __test_create('localhost')
        __test_create('test[01-09].host')

    def test_edit(self):
        def __test_edit(host_pattern, edit_key, edit_value):
            conf.init()
            nodesolo('edit', host_pattern, edit_key, edit_value)
            for host in util.get_available_hosts(host_pattern):
                host_json = util.load_json(host)
                self.assertEqual(edit_value, host_json[edit_key])

        __test_edit('localhost', 'run_list', 'recipe[test]')
        __test_edit('test0[6-9]*', 'run_list', 'recipe[test]')

    def test_remove(self):
        def __test_remove(host_pattern):
            conf.init()
            nodesolo('remove', host_pattern)
            for host in util.get_expanded_hosts(host_pattern):
                self.assertFalse(util.exists_json(host))

        __test_remove('test0[6-7]*')
        __test_remove('test0[7-9]*')

    def test_upload(self):
        def __test_upload(host_pattern):
            conf.init()
            nodesolo('upload', host_pattern)
            hosts = util.get_available_hosts(host_pattern)
            cmds = []
            for host in hosts:
                cmds.append('cmd> knife node from file {0}/{1}.json'.format(conf.NODE_DIR, host))
            self.assertEqual(cmds, env.cmd_history)

        __test_upload('localhost')
        __test_upload('test0[1-8]*')

    def test_download(self):
        def __test_download(host_pattern):
            conf.init()
            nodesolo('download', host_pattern)
            searched_nodes = testtools.get_searched_nodes_obj(host_pattern)
            nodes = searched_nodes['rows']
            for n in nodes:
                self.assertEqual(n, util.load_node_json(n['name']))

        __test_download('downloded.host')


