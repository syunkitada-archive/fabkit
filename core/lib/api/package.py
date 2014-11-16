# coding: utf-8

from fabric.api import warn_only
from api import *  # noqa
import filer
from lib import log


def install(package_name, path=None, option=''):
    with warn_only():
        if run('which yum').return_code == 0:
            result = run('rpm -q {0}'.format(package_name), warn_only=True)
            if not result.return_code == 0:
                if path:
                    result = sudo('yum install {0} -y {1}'.format(path, option))
                else:
                    result = sudo('yum install {0} -y {1}'.format(package_name, option))
                if result.return_code != 0:
                    msg = 'Failed install {0}.'.format(package_name)
                    log.error(msg)
                    raise Exception(msg)

        else:
            msg = 'It does not support the package manager of remote os.'
            log.error(msg)
            raise Exception(msg)


def register_repo(name, baseurl, gpgkey, gpgcheck=1):
    with warn_only():
        if run('which yum').return_code == 0:
            filer.file('/etc/yum.repos.d/{0}.repo'.format(name), src_str='''
[{0}]
name={0}
baseurl={1}
gpgkey={2}
gpgcheck={3}'''.format(name, baseurl, gpgkey, gpgcheck))

        else:
            msg = 'It does not support the package manager of remote os.'
            log.error(msg)
            raise Exception(msg)


def upgrade(name=''):
    with warn_only():
        if run('which yum').return_code == 0:
            sudo('yum upgrade {0} -y'.format(name))
        else:
            msg = 'It does not support the package manager of remote os.'
            log.error(msg)
            raise Exception(msg)
