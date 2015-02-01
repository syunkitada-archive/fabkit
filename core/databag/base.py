# coding: utf-8

from fabkit import api, databag as bag


@api.task
@api.hosts('localhost')
def databag(option=None, key=None, value=None):
    if option in ['set', 's']:
        bag.set(key, value)
        print 'set key:{0}, value:{1}'.format(key, value)

    elif option in ['get', 'g']:
        result = bag.get(key)
        print result
        return result

    elif option in ['list', 'l']:
        bag.print_list(key)

    else:
        print '"{0}" is bad option'.format(option)
        print databag.__doc__
