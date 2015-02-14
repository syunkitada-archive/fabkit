# coding: utf-8

"""
This module is manage state of node, fabscript and cluster.

status code is 0 or 3-digit number.
"""

# common
SUCCESS = 0

# node status
REGISTERED = 100
REGISTERED_MSG = 'registered'
START = 101
START_MSG = 'start: {0}'

# fabscript status
FABSCRIPT_SUCCESS_MSG = 'success {0}'
FABSCRIPT_FAILED_MSG = 'failed {0}'
FABSCRIPT_END_EMPTY_MSG = 'run empty'
FABSCRIPT_REGISTERED = 200
FABSCRIPT_REGISTERED_MSG = 'registered fabscript: {0}.{1}'
FABSCRIPT_START = 201
FABSCRIPT_START_MSG = 'start {0}'

# check status
SUCCESS_CHECK_MSG = 'Success check.'
FAILED_CHECK = 400
FAILED_CHECK_MSG = 'Failed check.'
FAILED_CHECK_SSH = 401
FAILED_CHECK_SSH_MSG = 'Failed check ssh.'
FAILED_CHECK_PING = 404
FAILED_CHECK_PING_MSG = 'Failed check ping.'

# sync status
SYNC_UPDATED = 701
SYNC_CREATED = 702
SYNC_REJECTED = 710

IS_NOT_SETUPED = 400
NODE_DOES_NOT_EXIST = 401
FABSCRIPT_DOES_NOT_EXIST = 402
RESULT_DOES_NOT_EXIST = 403
