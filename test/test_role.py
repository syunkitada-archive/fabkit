import unittest
from role import role
import conf

class TestSequenceFunctions(unittest.TestCase):
    def test_role(self):
        conf.init_test_conf()
        role_infos = [
                    {
                        'name': 'test01',
                        'run_list': ['recipe[test1]']
                    }, {
                        'name': 'test02',
                        'run_list': ['role[test01]', 'recipe[test2]']
                    }
                ]
        self.assertEqual(role_infos, role())

        role_infos = [
                    {
                        'name': 'test01',
                        'run_list': ['recipe[test1]']
                    }
                ]
        self.assertEqual(role_infos, role('*01'))
