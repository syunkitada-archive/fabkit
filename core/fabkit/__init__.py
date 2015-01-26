# coding: utf-8


from fabric import api
env = api.env

from shell import *  # noqa
from task import task  # noqa
from filer import Editor  # noqa
from package import repository, Package, Service  # noqa
