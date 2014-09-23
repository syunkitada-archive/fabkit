# coding: utf-8

from lib.api import *  # noqa
import platform


def start(package_name):
    os = platform.platform()
    if os.find('centos') >= 0:
        cmd_start = 'service {0} start'.format(package_name)

    sudo(cmd_start)


def enable(package_name):
    os = platform.platform()
    if os.find('centos') >= 0:
        cmd_enable = 'chkconfig {0} on'.format(package_name)

    sudo(cmd_enable)
