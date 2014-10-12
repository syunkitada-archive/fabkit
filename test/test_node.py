import unittest
from fabric.api import env
from node import (node,
                  chefnode)
from lib import util
from lib import conf


class TestNode(unittest.TestCase):

    def test_create(self):
        node('remove', '*')

        def __test_create(host_pattern):
            conf.init()
            node('create', host_pattern)
            for host in util.get_expanded_hosts(host_pattern):
                tmp_node = util.convert_node()
                tmp_node.update({'path': host})
                self.assertEqual(tmp_node, util.load_node(host))

        __test_create('localhost')
        __test_create('test[01-09].host')

    def test_edit(self):
        def __test_edit(host_pattern, edit_key, edit_value, result_value):
            conf.init()
            node('edit', host_pattern, edit_key, edit_value)
            for host in util.get_available_hosts(host_pattern):
                tmp_node = util.load_node(host)
                self.assertEqual(result_value, tmp_node[edit_key])

        __test_edit('localhost', 'fabrun_list', 'hello.world', ['hello.world'])
        __test_edit('test0[6-9]*', 'fabrun_list', 'hello.world', ['hello.world'])

    def test_remove(self):
        def __test_remove(host_pattern):
            conf.init()
            node('remove', host_pattern)
            for host in util.get_expanded_hosts(host_pattern):
                self.assertFalse(util.exists_node(host))

        __test_remove('test0[6-7]*')
        __test_remove('test0[7-9]*')

    def test_node(slef):
        conf.init()
        node()

    def test_chefnode(self):
        conf.init()
        host = 'localhost'
        chefnode(host)
        cmd_history = get_chefnode_cmds(host)
        self.assertEqual(env.cmd_history, cmd_history)
        self.assertEqual(env.hosts, [host])
        util.print_node_map()

    def test_chefbootstrap(self):
        def __test_bootstrap(host_pattern):
            conf.init()
            chefnode('bootstrap', host_pattern)
            cmd_history = []
            for host in util.get_expanded_hosts(host_pattern):
                cmd_history.append(
                    'local> knife bootstrap {0} -x {1} -N {0} --sudo '.format(host, env.user)  # noqa
                )
            self.assertEqual(cmd_history, env.cmd_history)

        __test_bootstrap('test0[6-7]')
        __test_bootstrap('localhost')


def get_chefnode_cmds(host):
    search_cmd = 'cmd> knife search node "name:{0}" -F json'.format(host)
    return [search_cmd]
