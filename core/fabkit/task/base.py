# coding: utf-8

from functools import wraps
from fabkit import env, filer, conf, status
from check_util import check_basic


def task(function=None, is_bootstrap=True):
    def wrapper(func):
        @wraps(func)
        def sub_wrapper(*args, **kwargs):
            env.node = env.node_map[env.host]
            env.node.update(env.node_status_map[env.host]['fabscript_map'][env.script_name])
            if is_bootstrap:
                bootstrap_status = env.node_map[env.host]['bootstrap_status']
                if not bootstrap_status == status.SUCCESS:
                    result = check_basic()
                    if result['task_status'] != status.SUCCESS:
                        return result

                    filer.mkdir(conf.REMOTE_DIR, owner='{0}:root'.format(env.user), mode='770')
                    filer.mkdir(conf.REMOTE_STORAGE_DIR, owner='{0}:root'.format(env.user),
                                mode='770')
                    filer.mkdir(conf.REMOTE_TMP_DIR, owner='{0}:root'.format(env.user),
                                mode='770')

            result = func(*args, **kwargs)
            if result is None:
                result = {}

            result['node'] = env.node

            return result

        # wrapper.__doc__ = func.__doc__
        # wrapper.__name__ = func.__name__
        # wrapper.__module__ = func.__module__
        sub_wrapper.is_task = True
        sub_wrapper.is_bootstrap = is_bootstrap
        return sub_wrapper

    if function:
        return wrapper(function)
    else:
        return wrapper
