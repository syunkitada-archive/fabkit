# coding: utf-8

from api import *  # noqa
import platform


def install(package_name, path=None):
    os = platform.platform()
    if os.find('centos') >= 0:
        result = run('rpm -q {0}'.format(package_name))
        if not result.return_code == 0:
            if path:
                sudo('yum install {0} -y'.format(path))
            else:
                sudo('yum install {0} -y'.format(package_name))
