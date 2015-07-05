# coding: utf-8

from fabkit import api, log, run, sudo


class Package():
    def __init__(self, package_name, path=None):
        self.package_name = package_name
        self.path = path

    def install(self, option=''):
        with api.warn_only():
            if run('which yum').return_code == 0:
                result = run('rpm -q {0}'.format(self.package_name), warn_only=True)
                if not result.return_code == 0:
                    if self.path:
                        result = sudo('yum install {0} -y {1}'.format(self.path, option))
                    else:
                        result = sudo('yum install {0} -y {1}'.format(self.package_name, option))
                    if result.return_code != 0:
                        msg = 'Failed install {0}.'.format(self.package_name)
                        log.error(msg)
                        raise Exception(msg)

            else:
                msg = 'It does not support the package manager of remote os.'
                log.error(msg)
                raise Exception(msg)

        return self

    def uninstall(self):
        with api.warn_only():
            if run('which yum').return_code == 0:
                sudo('yum remove {0} -y'.format(self.package_name))
            else:
                msg = 'It does not support the package manager of remote os.'
                log.error(msg)
                raise Exception(msg)

        return self

    def upgrade(self):
        with api.warn_only():
            if run('which yum').return_code == 0:
                sudo('yum upgrade {0} -y'.format(self.package_name))
            else:
                msg = 'It does not support the package manager of remote os.'
                log.error(msg)
                raise Exception(msg)

        return self
