# coding: utf-8

from api import sudo
from types import IntType


def a(*args, **kwargs):
    append(*args, **kwargs)


def append(file_path, txt, start=None, end=None):
    # TODO 正規表現による行指定も冪等性持ってできるようにする
    if start:
        if end:
            if type(start) is IntType:
                result_start = sudo('sed -n "{0}p" {1}'.format(start + 1, file_path))
                result_end = sudo('sed -n "{0}p" {1}'.format(end + 1, file_path))

                if result_start != txt and result_end != txt:
                    sudo('sed -i "{0},{1}a {2}" {3}'.format(start, end, txt, file_path))
        else:
            if type(start) is IntType:
                result = sudo('sed -n "{0}p" {1}'.format(start + 1, file_path))

                if result != txt:
                    sudo('sed -i "{0}a {1}" {2}'.format(start, txt, file_path))


def i(*args, **kwargs):
    insert(*args, **kwargs)


def insert(file_path, txt, start=None, end=None):
    # TODO 正規表現による行指定も冪等性持ってできるようにする
    if start:
        if end:
            if type(start) is IntType:
                result_start = sudo('sed -n "{0}p" {1}'.format(start, file_path))
                result_end = sudo('sed -n "{0}p" {1}'.format(end, file_path))
                if result_start != txt and result_end != txt:
                    sudo('sed -i "{0},{1}i {2}" {3}'.format(start, end, txt, file_path))
        else:
            if type(start) is IntType:
                result = sudo('sed -n "{0}p" {1}'.format(start, file_path))

                if result != txt:
                    sudo('sed -i "{0}i {1}" {2}'.format(start, txt, file_path))


def s(*args, **kwargs):
    substitute(*args, **kwargs)


def substitute(file_path, target, txt, start=None, end=None):
    # TODO sed s
    pass
