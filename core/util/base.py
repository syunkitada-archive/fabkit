# coding: utf-8

import os
import itertools
import subprocess
import sys
from fabkit import api, util
from pdns import pdnsapi
from oslo_config import generator, cfg
from oslo_messaging._drivers import amqp
from oslo_messaging._drivers import impl_rabbit
from oslo_db.options import database_opts
from oslo_log import _options
from fabkit.conf import conf_base, conf_fabric, conf_web, conf_test


list_opts = [
    ('DEFAULT',
     itertools.chain(
         conf_base.default_opts,
         conf_fabric.default_opts,
         _options.common_cli_opts,
         _options.logging_cli_opts,
     )),
    ('cluster',
     itertools.chain(
         conf_base.cluster_opts,
     )),
    ('client',
     itertools.chain(
         conf_base.client_opts,
     )),
    ('logger',
     itertools.chain(
         conf_base.logger_opts,
     )),
    ('node_logger',
     itertools.chain(
         conf_base.node_logger_opts,
     )),
    ('database',
     itertools.chain(
         database_opts,
     )),
    ('oslo_messaging_rabbit', itertools.chain(
        itertools.chain(amqp.amqp_opts, impl_rabbit.rabbit_opts))),
    ('web',
     itertools.chain(
         conf_web.web_opts,
     )),
    ('test',
     itertools.chain(
         conf_test.test_opts,
     )),
]

output_file = ''
wrap_width = 70

CONF = cfg.CONF


@api.task
def genconfig(conf_file='fabfile.ini.sample'):
    conf_file_path = os.path.join(CONF._repo_dir, conf_file)
    output_file = open(conf_file_path, 'w')
    formatter = generator._OptFormatter(output_file=output_file, wrap_width=wrap_width)

    formatter.write("#\n# fabfile.ini\n#\n")
    for section, opts in list_opts:
        formatter.write("\n\n")
        formatter.write("[{0}]\n".format(section))
        for opt in opts:
            formatter.write("\n")
            formatter.format(opt)


@api.task
def sync_fablib():
    util.git_clone_required_fablib()


@api.task
def sync_db(*args, **kwargs):
    if sys.exec_prefix == '/usr':
        prefix = ''
    else:
        prefix = '{0}/bin/'.format(sys.exec_prefix)

    if len(args) > 0 and args[0] == 'generate':
        msg = kwargs.get('m')
        if msg is None:
            msg = kwargs.get('msg')
        if msg is None:
            print 'Input messag. For example,\n$ fab syncdb:generate,m="update model"'
            return

        subprocess.call('cd {0} && {1}alembic revision --autogenerate -m "{2}"'.format(
            CONF._sqlalchemy_dir, prefix, msg), shell=True)

    else:
        subprocess.call('cd {0} && {1}alembic upgrade head'.format(
            CONF._sqlalchemy_dir, prefix), shell=True)

        subprocess.call('cd {0} && {1}alembic upgrade head'.format(
            CONF._pdns_sqlalchemy_dir, prefix), shell=True)

        subprocess.call("""cd {0} &&
{1}python manage.py makemigrations --noinput;
{1}python manage.py migrate --noinput;
        """.format(CONF._webapp_dir, prefix), shell=True)

        subprocess.call("""cd {0} &&
echo "
from django.contrib.auth.models import User, Group;
from django.core.exceptions import ObjectDoesNotExist;

try:
    user = User.objects.get(username='{username}');
    user.set_password('{password}')
    user.save()
    print 'Updated ' + user.username + ' user.'
except ObjectDoesNotExist:
    user = User.objects.create_superuser('{username}', '', '{password}')
    print 'Created ' + user.username + ' user.'

try:
    group = Group.objects.get(name='{group}');
    print user.username + ' group is already exists.'
except ObjectDoesNotExist:
    group = Group(name='{group}')
    group.save()
    print 'Created ' + group.name + ' group.'

try:
    user.groups.get(name=group.name)
    print group.name + ' is already exsits in ' + user.username + ' user.groups.'
except ObjectDoesNotExist:
    user.groups.add(group)
    user.save()
    print 'Added ' + group.name + ' group to ' + user.username + ' user.groups.'

" | {1}python manage.py shell;
        """.format(CONF._webapp_dir, prefix,
                   username=CONF.client.username, password=CONF.client.password,
                   group=CONF.client.group),
            shell=True)


@api.task
def create_dns_domain(name):
    pdns = pdnsapi.PdnsAPI()
    pdns.create_domain(name)


@api.task
def create_dns_record(name, domain_name, type, content):
    pdns = pdnsapi.PdnsAPI()
    if type == 'A':
        pdns.create_record(name, domain_name, type, content)
