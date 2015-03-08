# coding: utf-8

import unittest
from databag import databag


class TestDatabag(unittest.TestCase):

    def test_create(self):
        databag('set', 'test/database.password', 'dbpass')
        self.assertEqual(databag('get', 'test/database.password'), 'dbpass')
