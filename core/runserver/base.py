# coding: utf-8

from fabkit import api
import os
import subprocess
from oslo_config import cfg
import sys

CONF = cfg.CONF


@api.task
@api.hosts('localhost')
def runserver(*args, **kwargs):
    create_tls_cert()
    run_nodejs()
    run_grunt()
    run_server()


def local(cmd):
    subprocess.call(cmd, shell=True)


def create_tls_cert():
    return
    certdir = os.path.join(CONF._storage_dir, 'cert')
    certfile = os.path.join(certdir, 'server.crt')
    csrfile = os.path.join(certdir, 'server.csr')
    keyfile_tmp = os.path.join(certdir, 'server.key.tmp')
    keyfile = os.path.join(certdir, 'server.key')
    password = 'password'

    if not os.path.exists(certdir):
        os.mkdir(certdir)

    print '\nCreate private key: {0}'.format(keyfile_tmp)
    if not os.path.exists(keyfile_tmp):
        local('openssl genrsa -des3 -passout pass:{0} -out {1} 4096'.format(
            password, keyfile_tmp))
    else:
        print '{0} is already exists.'.format(keyfile_tmp)

    print '\nCreate Decryption private key: {0}'.format(keyfile)
    if not os.path.exists(keyfile):
        local('openssl rsa -passin pass:{0} -in {1} -out {2}'.format(
            password, keyfile_tmp, keyfile))
    else:
        print '{0} is already exists.'.format(keyfile)

    print '\nCreate CSR: {0}'.format(csrfile)
    if not os.path.exists(csrfile):
        local('openssl req -passin pass:{0} -new -key {1} -sha256 -out {2}'.format(
            password, keyfile_tmp, csrfile))
    else:
        print '{0} is already exists.'.format(csrfile)

    print '\nCreate SSL certificate (public key): {0}'.format(certfile)
    if not os.path.exists(certfile):
        local('openssl x509 -passin pass:{0} '
              '-in {1} -days 365 -req -signkey {2} -sha256 -out {3}'.format(
                  password, csrfile, keyfile_tmp, certfile))
    else:
        print '{0} is already exists.'.format(certfile)


def run_nodejs():
    cwd = os.path.join(CONF._webapp_dir, 'fabnode')
    subprocess.Popen(['coffee', 'main.coffee'], cwd=cwd)


def run_grunt():
    cwd = CONF._webapp_dir
    subprocess.Popen(['grunt'], cwd=cwd)


def run_server():
    cwd = CONF._webapp_dir

    if sys.exec_prefix == '/usr':
        prefix = ''
    else:
        prefix = '{0}/bin/'.format(sys.exec_prefix)

    subprocess.call(['{0}python'.format(prefix), 'manage.py', 'runserver_plus',
                     '0.0.0.0:{0}'.format(CONF.web.port)], cwd=cwd)
