# coding: utf-8

from fabkit import sudo, env, log, api


class Service():
    def __init__(self, name):
        self.name = name
        self.result = None

    def unsupport(self):
        msg = 'It does not support the service manager of remote os.'
        log.error(msg)
        raise Exception(msg)

    def wrap_cmd(self, option, **kwargs):
        with api.warn_only():
            service_manager = env.node['service_manager']
            if service_manager == 'systemd':
                self.result = sudo('systemctl {0} {1}'.format(option, self.name), **kwargs)
            elif service_manager == 'initd':
                self.result = sudo('/etc/init.d/{1} {0}'.format(option, self.name), **kwargs)
            elif service_manager == 'upstart':
                self.result = sudo('initctl {0} {1}'.format(option, self.name), **kwargs)
            else:
                self.unsupport()
            return self

    def start(self, **kwargs):
        return self.wrap_cmd('start')

    def stop(self, **kwargs):
        return self.wrap_cmd('stop')

    def restart(self, **kwargs):
        return self.wrap_cmd('restart')

    def reload(self, **kwargs):
        return self.wrap_cmd('reload')

    def status(self, **kwargs):
        return self.wrap_cmd('status')

    def enable(self, **kwargs):
        with api.warn_only():
            service_manager = env.node['service_manager']
            if service_manager == 'systemd':
                self.result = sudo('systemctl enable {0}'.format(self.name), **kwargs)
            elif service_manager == 'initd':
                self.result = sudo('chkconfig {0} on'.format(self.name), **kwargs)
            else:
                self.unsupport()

        return self

    def disable(self, **kwargs):
        with api.warn_only():
            service_manager = env.node['service_manager']
            if service_manager == 'systemd':
                self.result = sudo('systemctl disable {0}'.format(self.name), **kwargs)
            elif service_manager == 'initd':
                self.result = sudo('chkconfig {0} off'.format(self.name), **kwargs)
            else:
                self.unsupport()

        return self
