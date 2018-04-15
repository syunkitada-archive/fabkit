# coding: utf-8


from functools import wraps
from fabric import api
env = api.env
parallel = api.parallel
serial = api.serial
put = api.put


def system_task(func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with api.hide(*CONF.system_output_filter):
            return func(*args, **kwargs)

    return wrapper


from shell import *  # noqa
from task import task  # noqa
from system import Observer, Package, Service, user, group  # noqa
from filer import Editor  # noqa
