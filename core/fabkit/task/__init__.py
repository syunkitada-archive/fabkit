# coding: utf-8

from fabkit import api
from types import DictType


@api.task
@api.runs_once
def task(func):
    def wrapper(*args, **kwargs):
        default_result = {
            'state': 1,
            'msg': 'Success',
            'task_state': 0,
        }

        results = api.execute(func, *args, **kwargs)
        for host, result in results.items():
            if not result or type(result) != DictType:
                result = default_result
                results[host] = result

        return results

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.is_task = True
    return wrapper
