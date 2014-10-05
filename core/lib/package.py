# coding: utf-8

from lib.api import *  # noqa


def install(package_name, path=None):
    # TODO os判定
    result = run('rpm -q {0}'.format(package_name))
    if not result.return_code == 0:
        if path:
            sudo('yum install {0} -y'.format(path))
        else:
            sudo('yum install {0} -y'.format(package_name))
