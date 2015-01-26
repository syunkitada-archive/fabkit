# coding: utf-8

from fabkit import sudo


class Service():
    def __init__(self, name):
        self.name = name

    def start(self, **kwargs):
        sudo('/etc/init.d/{0} start'.format(self.name), **kwargs)
        return self

    def stop(self, **kwargs):
        sudo('/etc/init.d/{0} stop'.format(self.name), **kwargs)
        return self

    def restart(self, **kwargs):
        sudo('/etc/init.d/{0} restart'.format(self.name), **kwargs)
        return self

    def reload(self, **kwargs):
        sudo('/etc/init.d/{0} reload'.format(self.name), **kwargs)
        return self

    def enable(self, **kwargs):
        sudo('chkconfig {0} on'.format(self.name), **kwargs)
        return self

    def disable(self):
        sudo('chkconfig {0} off'.format(self.name))
        return self
