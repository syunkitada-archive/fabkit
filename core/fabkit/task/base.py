# coding: utf-8

from functools import wraps
from fabkit import env, filer, conf, status
from check_util import check_basic


def task(function=None, is_bootstrap=True):
    def wrapper(func):
        @wraps(func)
        def sub_wrapper(*args, **kwargs):
            env.node.update(env.node_status_map[env.host]['fabscript_map'][env.script_name])
            if is_bootstrap:
                result = check_basic()
                if result['task_status'] != status.SUCCESS:
                    return result

                filer.mkdir(conf.REMOTE_DIR)
                filer.mkdir(conf.REMOTE_STORAGE_DIR)
                filer.mkdir(conf.REMOTE_TMP_DIR, mode='777')

            return func(*args, **kwargs)

        # wrapper.__doc__ = func.__doc__
        # wrapper.__name__ = func.__name__
        # wrapper.__module__ = func.__module__
        sub_wrapper.is_task = True
        return sub_wrapper

    if function:
        return wrapper(function)
    else:
        return wrapper
