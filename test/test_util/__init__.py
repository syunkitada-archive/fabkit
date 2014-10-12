# coding: utf-8

import unittest
from lib import util
import re
from test_util_host import TestUtilHost  # noqa
from test_util_node import TestUtilNode  # noqa


class TestUtil(unittest.TestCase):
    def test_get_timestamp(self):
        prog = re.compile('[1-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-2][0-9]:[0-6][0-9]:[0-6][0-9]')  # noqa
        self.assertTrue(prog.match(util.get_timestamp()))

    def test_confirm(self):
        self.assertTrue(util.confirm('Is ok?'))
        self.assertTrue(util.confirm('Is ok?', 'Canceled'))
