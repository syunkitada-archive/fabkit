# coding: utf-8

from fabkit import api, env, filer, conf, status
from check_util import check_basic


@api.task
@api.runs_once
def task(is_bootstrap=True):

    def sub_task(func):
        def wrapper(*args, **kwargs):
            env.node = {}
            if is_bootstrap:
                result = check_basic()
                if result['task_status'] != status.SUCCESS:
                    return result

                filer.mkdir(conf.REMOTE_DIR)
                filer.mkdir(conf.REMOTE_STORAGE_DIR)
                filer.mkdir(conf.REMOTE_TMP_DIR, mode='777')

            return func(*args, **kwargs)

        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__
        wrapper.__module__ = func.__module__
        wrapper.is_task = True
        return wrapper

    return sub_task
