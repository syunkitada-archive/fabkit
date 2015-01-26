# coding: utf-8

from fabkit import api, filer, log, run


def register(name, baseurl, gpgkey, gpgcheck=1):
    with api.warn_only():
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
