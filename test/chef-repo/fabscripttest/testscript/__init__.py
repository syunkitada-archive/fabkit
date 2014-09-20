# coding: utf-8
from fabric.api import (task,
                        hosts)
from api import run


@task
@hosts('localhost')
def test():
    run('hostname')
