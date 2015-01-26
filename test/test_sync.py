# coding: utf-8

import unittest
from sync import sync


class TestSync(unittest.TestCase):

    def test_sync(self):
        sync('dump')
        sync('merge')
