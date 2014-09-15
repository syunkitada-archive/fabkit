# coding: utf-8
from fabric.api import env, task, hosts
from api import *
from lib import util, conf


@task
@hosts('localhost')
def test():
    run('hostname')
