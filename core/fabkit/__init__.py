# coding: utf-8


from fabric import api
env = api.env
parallel = api.parallel
serial = api.serial

from shell import *  # noqa
from system import Package, Service  # noqa
from task import task  # noqa
from filer import Editor  # noqa
