# coding: utf-8

from api import *  # noqa
from fabric.api import warn_only


def add(name):
    with warn_only():
        passwd = run('cat /etc/passwd | grep ^{0}:'.format(name))
        if passwd.return_code != 0:
            sudo('useradd {0} -M'.format(name))
