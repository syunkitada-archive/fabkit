# coding: utf-8

import sys
import traceback
from functools import wraps
from fabkit import api, env, filer, status, log
from check_util import check_basic
from oslo_config import cfg

CONF = cfg.CONF


def task(function=None, is_bootstrap=True):
    def wrapper(func):
        @wraps(func)
        def sub_wrapper(*args, **kwargs):
            env.args = args if args else []
            env.kwargs = kwargs if kwargs else {}
            env.node = env.node_map[env.host]
            env.node.update(env.node_status_map[env.host]['fabscript_map'][env.script_name])
            kwargs = env.host_script_map.get(env.host, {}).get(env.script_name, {})
            if is_bootstrap:
                bootstrap_status = env.node_map[env.host]['bootstrap_status']
                if not bootstrap_status == status.SUCCESS:
                    with api.hide(*CONF.system_output_filter):
                        result = check_basic()
                        if result['task_status'] != status.SUCCESS:
                            result['node'] = env.node
                            return result

                    filer.mkdir(CONF._remote_dir, owner='{0}:root'.format(env.user), mode='770')
                    filer.mkdir(CONF._remote_storage_dir, owner='{0}:root'.format(env.user),
                                mode='770')
                    filer.mkdir(CONF._remote_tmp_dir, owner='{0}:root'.format(env.user),
                                mode='770')

            try:
                result = func(**kwargs)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                msg = traceback.format_exception(exc_type, exc_value, exc_traceback)
                log.error(''.join(msg))
                result = {
                    'task_status': status.FAILED
                }

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
