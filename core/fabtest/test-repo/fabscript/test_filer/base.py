# cording: utf-8

from fabkit import task, filer


@task
def setup():
    filer.mkdir('/tmp/fabkit')
    print 'test'


@task
def hello():
    print 'hello'
