# coding: utf-8


from fabric import api
env = api.env
parallel = api.parallel
serial = api.serial
put = api.put

from shell import *  # noqa
from system import Observer, Package, Service, user, group  # noqa
from task import task  # noqa
from filer import Editor  # noqa
