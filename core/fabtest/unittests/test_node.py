# coding: utf-8

import unittest
from node import node  # noqa
from setup import setup, manage  # noqa


class TestUtilNode(unittest.TestCase):
    def test_node(self):
        node()
        node('r')
        node('e')
