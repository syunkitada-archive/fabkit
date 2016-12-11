# coding: utf-8

from fabkit import api, sudo


def add(name, gid=None):
    with api.warn_only():
        getent = sudo('getent group | grep ^{0}:'.format(name))
        if getent.return_code != 0:
            if gid is None:
                sudo('groupadd {0}'.format(name))
            else:
                sudo('groupadd -g {0} {1}'.format(gid, name))
