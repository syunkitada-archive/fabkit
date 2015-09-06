# coding: utf-8

from fabkit import sudo
from types import IntType


class Editor():
    def __init__(self, file_path):
        self.file_path = file_path

    def a(self, *args, **kwargs):
        return self.append(*args, **kwargs)

    def append(self, txt, start=None, end=None):
        # TODO 正規表現による行指定も冪等性持ってできるようにする
        if start:
            if end:
                if type(start) is IntType:
                    result_start = sudo('sed -n "{0}p" {1}'.format(start + 1, self.file_path))
                    result_end = sudo('sed -n "{0}p" {1}'.format(end + 1, self.file_path))

                    if result_start != txt and result_end != txt:
                        sudo('sed -i "{0},{1}a {2}" {3}'.format(start, end, txt, self.file_path))
            else:
                if type(start) is IntType:
                    result = sudo('sed -n "{0}p" {1}'.format(start + 1, self.file_path))

                    if result != txt:
                        sudo('sed -i "{0}a {1}" {2}'.format(start, txt, self.file_path))
        else:
            sudo('grep "{0}" {1} || echo "{0}" >> {1}'.format(txt, self.file_path))

        return self

    def i(self, *args, **kwargs):
        return self.insert(*args, **kwargs)

    def insert(self, txt, start=None, end=None):
        # TODO 正規表現による行指定も冪等性持ってできるようにする
        if start:
            if end:
                if type(start) is IntType:
                    result_start = sudo('sed -n "{0}p" {1}'.format(start, self.file_path))
                    result_end = sudo('sed -n "{0}p" {1}'.format(end, self.file_path))
                    if result_start != txt and result_end != txt:
                        sudo('sed -i "{0},{1}i {2}" {3}'.format(start, end, txt, self.file_path))
            else:
                if type(start) is IntType:
                    result = sudo('sed -n "{0}p" {1}'.format(start, self.file_path))

                    if result != txt:
                        sudo('sed -i "{0}i {1}" {2}'.format(start, txt, self.file_path))

        return self

    def s(self, *args, **kwargs):
        return self.substitute(*args, **kwargs)

    def substitute(self, target, txt, start=None, end=None):
        # TODO sed s
        return self
