# coding: utf-8

from fabric.api import task, hosts
from lib import api


@task
@hosts('localhost')
def databag(option=None, key=None, value=None):
    if option == 'set':
        api.databag.set(key, value)
        print 'set key:{0}, value:{1}'.format(key, value)

    elif option == 'get':
        print api.databag.get(key)
