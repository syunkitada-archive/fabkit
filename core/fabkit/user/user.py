# coding: utf-8

from fabkit import api, run, sudo


def add(name, group=None):
    with api.warn_only():
        passwd = run('cat /etc/passwd | grep ^{0}:'.format(name))
        if passwd.return_code != 0:
            sudo('useradd {0} -M -s/bin/false'.format(name))

        if group is not None:
            sudo('gpasswd -add {0} {1}'.format(name, group))
