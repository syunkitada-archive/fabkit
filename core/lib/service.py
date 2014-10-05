# coding: utf-8

from lib.api import *  # noqa


# TODO osの判定
def start(package_name):
    cmd_start = 'service {0} start'.format(package_name)

    sudo(cmd_start)


def enable(package_name):
    cmd_enable = 'chkconfig {0} on'.format(package_name)

    sudo(cmd_enable)
