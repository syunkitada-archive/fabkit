# coding: utf-8

from fabkit import api, log, run, sudo, env


class Package():
    def __init__(self, package_name, path=None):
        self.package_name = package_name
        self.path = path
        self.result = None

    def unsupport(self):
        msg = 'It does not support the package manager of remote os.'
        log.error(msg)
        self.result = None
        raise Exception(msg)

    def install(self, option=''):
        with api.warn_only():
            if env.node['package_manager'] == 'yum':
                result = run('rpm -q {0}'.format(self.package_name), warn_only=True)
                if not result.return_code == 0:
                    if self.path:
                        self.result = sudo('yum install {0} -y {1}'.format(self.path, option))
                    else:
                        self.result = sudo('yum install {0} -y {1}'.format(
                            self.package_name, option))

            elif env.node['package_manager'] == 'apt':
                result = run('dpkg -l {0}'.format(self.package_name), warn_only=True)
                if not result.return_code == 0:
                    if self.path:
                        self.result = sudo('apt-get install {0} -y {1}'.format(self.path, option))
                    else:
                        self.result = sudo('apt-get install {0} -y {1}'.format(
                            self.package_name, option))
            else:
                self.unsupport()

        if self.result.return_code != 0:
            msg = 'Failed install {0}.'.format(self.package_name)
            log.error(msg)
            raise Exception(msg)

        return self

    def uninstall(self):
        with api.warn_only():
            if env.node['package_manager'] == 'yum':
                self.result = sudo('yum remove {0} -y'.format(self.package_name))
            elif env.node['package_manager'] == 'apt':
                self.result = sudo('apt-get autoremove {0} -y'.format(self.package_name))
            else:
                self.unsupport()

        if self.result.return_code != 0:
            msg = 'Failed uninstall {0}.'.format(self.package_name)
            log.error(msg)
            raise Exception(msg)

        return self

    def upgrade(self):
        with api.warn_only():
            if env.node['package_manager'] == 'yum':
                self.result = sudo('yum upgrade {0} -y'.format(self.package_name))
            elif env.node['package_manager'] == 'apt':
                self.result = sudo('apt-get upgrade {0} -y'.format(self.package_name))
            else:
                self.unsupport()

        if self.result.return_code != 0:
            msg = 'Failed upgrade {0}.'.format(self.package_name)
            log.error(msg)
            raise Exception(msg)

        return self
