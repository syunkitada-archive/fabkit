# coding: utf-8

from fabkit import task, run, sudo


@task
def setup():
    run('date > /etc/motd')


@task
def setup2():
    run('date >> /etc/motd')


@task
def restart():
    sudo('service crond restart')


@task
def check_service():
    sudo('service crond status')
