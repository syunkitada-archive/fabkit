# coding: utf-8

from fabkit import api, local
import os
from oslo_config import cfg
from eventlet import wsgi
import eventlet

CONF = cfg.CONF


@api.task
@api.hosts('localhost')
def runserver(*args, **kwargs):
    len_args = len(args)
    certdir = os.path.join(CONF._storage_dir, 'cert')
    certfile = os.path.join(certdir, 'server.crt')
    csrfile = os.path.join(certdir, 'server.csr')
    keyfile_tmp = os.path.join(certdir, 'server.key.tmp')
    keyfile = os.path.join(certdir, 'server.key')

    if len_args > 0 and 'create_cert' in args:
        if not os.path.exists(certdir):
            os.mkdir(certdir)

        print '\nCreate private key: {0}'.format(keyfile_tmp)
        if not os.path.exists(keyfile_tmp):
            local('openssl genrsa -aes128 -out {0} 4096'.format(keyfile_tmp))
        else:
            print '{0} is already exists.'.format(keyfile_tmp)

        print '\nCreate CSR: {0}'.format(csrfile)
        if not os.path.exists(csrfile):
            local('openssl req -new -key {0} -sha256 -out {1}'.format(keyfile_tmp, csrfile))
        else:
            print '{0} is already exists.'.format(csrfile)

        print '\nCreate SSL certificate (public key): {0}'.format(certfile)
        if not os.path.exists(certfile):
            local('openssl x509 -in {0} -days 365 -req -signkey {1} -sha256 -out {2}'.format(
                csrfile, keyfile_tmp, certfile))
        else:
            print '{0} is already exists.'.format(certfile)

        print '\nCreate Decryption private key: {0}'.format(keyfile)
        if not os.path.exists(keyfile):
            local('openssl rsa -in {0} -out {1}'.format(keyfile_tmp, keyfile))
        else:
            print '{0} is already exists.'.format(keyfile)

        return

    from django.core.wsgi import get_wsgi_application
    import pymysql
    pymysql.install_as_MySQLdb()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_conf.settings")
    application = get_wsgi_application()

    wsgi.server(eventlet.listen(('', 8080)), application)
