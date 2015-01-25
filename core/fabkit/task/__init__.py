# coding: utf-8


def task(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.is_task = True
    return wrapper
