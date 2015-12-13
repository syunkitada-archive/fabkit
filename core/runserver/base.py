# coding: utf-8

from fabkit import api, local
import os
from oslo_config import cfg

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

    if len_args == 1 and args[0] == 'create_cert':
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

        exit(0)

    import eventlet
    import eventlet.wsgi
    from web_conf.wsgi import application

    # server_sock = eventlet.listen(('0.0.0.0', 8080))
    # eventlet.wsgi.server(server_sock, application)
    port = int(kwargs.get('port', CONF.web.port))
    is_https = bool(kwargs.get('is_https', CONF.web.is_https))

    server_sock = eventlet.listen(('', port))

    if is_https:
        eventlet.wsgi.server(eventlet.wrap_ssl(server_sock,
                                               certfile=certfile,
                                               keyfile=keyfile,
                                               server_side=True),
                             application)
    else:
        eventlet.wsgi.server(server_sock, application)
