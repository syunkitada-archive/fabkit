# coding: utf-8

import unittest
from node import node  # noqa
from setup import setup, manage  # noqa


class TestUtilNode(unittest.TestCase):
    def test_node(self):
        self.assertEqual(
            'hello', 'hello'
        )

        node()
        node('r')
        node('e')

    def test_filer(self):
        node('test_filer/')
        setup()
        manage('hello')
