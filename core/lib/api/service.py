# coding: utf-8

from api import *  # noqa


def start(package_name):
    sudo('/etc/init.d/{0} start'.format(package_name))


def stop(package_name):
    sudo('/etc/init.d/{0} restart'.format(package_name))


def restart(package_name):
    sudo('/etc/init.d/{0} restart'.format(package_name))


def enable(package_name):
    sudo('chkconfig {0} on'.format(package_name))


def disable(package_name):
    sudo('chkconfig {0} off'.format(package_name))
