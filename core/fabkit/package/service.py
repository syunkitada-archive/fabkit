# coding: utf-8

import re
from fabkit import sudo, api, env

re_centos7 = re.compile('CentOS 7.*')


class Service():
    def __init__(self, name):
        self.name = name

    def start(self, **kwargs):
        node_os = env.node['os']
        if re_centos7.match(node_os):
            sudo('systemctl start {0}'.format(self.name, **kwargs))
        else:
            sudo('/etc/init.d/{0} start'.format(self.name), **kwargs)
        return self

    def stop(self, **kwargs):
        node_os = env.node['os']
        if re_centos7.match(node_os):
            sudo('systemctl stop {0}'.format(self.name, **kwargs))
        else:
            sudo('/etc/init.d/{0} stop'.format(self.name), **kwargs)
        return self

    def restart(self, **kwargs):
        node_os = env.node['os']
        if re_centos7.match(node_os):
            sudo('systemctl restart {0}'.format(self.name, **kwargs))
        else:
            sudo('/etc/init.d/{0} restart'.format(self.name), **kwargs)
        return self

    def reload(self, **kwargs):
        node_os = env.node['os']
        if re_centos7.match(node_os):
            sudo('systemctl reload {0}'.format(self.name, **kwargs))
        else:
            sudo('/etc/init.d/{0} reload'.format(self.name), **kwargs)
        return self

    def status(self, **kwargs):
        node_os = env.node['os']
        with api.warn_only():
            if re_centos7.match(node_os):
                result = sudo('systemctl status {0}'.format(self.name, **kwargs))
            else:
                result = sudo('/etc/init.d/{0} status'.format(self.name), **kwargs)
            return result

    def enable(self, **kwargs):
        node_os = env.node['os']
        if re_centos7.match(node_os):
            sudo('systemctl enable {0}'.format(self.name), **kwargs)
        else:
            sudo('chkconfig {0} on'.format(self.name), **kwargs)
        return self

    def disable(self, **kwargs):
        node_os = env.node['os']
        if re_centos7.match(node_os):
            sudo('systemctl disable {0}'.format(self.name), **kwargs)
        else:
            sudo('chkconfig {0} off'.format(self.name))
        return self
