# coding: utf-8

from fabkit import api, databag as bag


@api.task
@api.hosts('localhost')
def databag(option=None, key=None, value=None):
    if option == 'set':
        bag.set(key, value)
        print 'set key:{0}, value:{1}'.format(key, value)

    elif option == 'get':
        result = bag.get(key)
        print result
        return result

    elif option == 'list':
        print 'list'
