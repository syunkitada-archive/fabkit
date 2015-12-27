# cording: utf-8

from fabkit import task, filer, run


@task
def setup():
    filer.mkdir('/tmp/fabkit')
    filer.file(src='file_sample.txt', dest='/tmp/fabkit/file_sample.txt',
               override=True)
    filer.template(src='template_sample.txt',
                   dest='/tmp/fabkit/template_sample.txt', data={'msg': 'test'})
    run('diff /tmp/fabkit/file_sample.txt /tmp/fabkit/template_sample.txt')


@task
def hello():
    print 'hello'
