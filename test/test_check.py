# coding: utf-8

import unittest
from fabric.api import env
from check import check
from lib import (conf,
                 util)
import platform
from node import node


class TestCheck(unittest.TestCase):
    def test_remote_check(self):
        node('remove', '*')
        conf.init()

        node('create', 'localhost')
        check()
        self.assertEqual(get_check_cmds(), env.cmd_history)

    def test_log_check(self):
        # TODO logが正常時、エラー時のテスト
        node('remove', '*')
        conf.init()
        host = 'localhost'
        tmp_node = util.convert_node_log()
        tmp_node.update({'path': host})
        tmp_node.update({'ipaddress': '192.168.11.11'})
        tmp_node.update({'ssh': 'failed'})
        tmp_node.update({'last_cook': ''})
        tmp_node.update({'last_fabcooks': ''})
        tmp_node.update({'last_runs': ''})
        util.dump_node(host, tmp_node)
        check()


def get_check_cmds():
    if platform.platform().find('CYGWIN') >= 0:
        cmd_ping = 'ping {0} -n 1 -w 2'
    else:
        cmd_ping = 'ping {0} -c 1 -W 2'

    return [
        'cmd> {0}'.format(cmd_ping.format(env.host)),
        'run> uptime',
    ]
