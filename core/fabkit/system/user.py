# coding: utf-8

from fabkit import api, sudo
import group as group_mod


def add(name, uid=None, group=None, gid=None):
    with api.warn_only():
        getent = sudo('getent passwd | grep ^{0}:'.format(name))
        if getent.return_code != 0:
            group_option = ''
            if group is not None:
                group_mod.add(group, gid=gid)
                group_option = '-g {0}'.format(group)

            if uid is None:
                sudo('useradd -M -s/bin/false {0} {1}'.format(name, group_option))
            else:
                sudo('useradd -M -s/bin/false -u {1} {0} {2}'.format(name, uid, group_option))
