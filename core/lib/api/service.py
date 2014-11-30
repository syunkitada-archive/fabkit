# coding: utf-8

from api import *  # noqa


def start(package_name, **kwargs):
    sudo('/etc/init.d/{0} start'.format(package_name), **kwargs)


def stop(package_name, **kwargs):
    sudo('/etc/init.d/{0} stop'.format(package_name), **kwargs)


def restart(package_name, **kwargs):
    sudo('/etc/init.d/{0} restart'.format(package_name), **kwargs)


def reload(package_name, **kwargs):
    sudo('/etc/init.d/{0} reload'.format(package_name), **kwargs)


def enable(package_name, **kwargs):
    sudo('chkconfig {0} on'.format(package_name), **kwargs)


def disable(package_name):
    sudo('chkconfig {0} off'.format(package_name))
