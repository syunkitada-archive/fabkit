# coding: utf-8

from oslo_config import cfg
from central import CentralAPI
from db import dbapi

CONF = cfg.CONF


def manage(*args, **kwargs):
    if 'help' in args:
        print 'help'

    elif 'setup' in args:
        centralapi = CentralAPI()
        result = centralapi.setup()
        print result

    elif 'test' in args:
        central_dbapi = dbapi.DBAPI()
        import datetime
        agent_data = {
            'agent_type': 'agent',
            'host': 'localhost',
            'heartbeat_timestamp': datetime.datetime.utcnow(),
            'status': 'active',
            'err_status': 'ok',
            'last_warn_errs_len': '',
            'last_crit_errs_len': '',
            'last_warn_errs': '',
            'last_crit_errs': '',
        }

        print central_dbapi.create_or_update_agent(agent_data)
        print central_dbapi.get_agent('agent', 'localhost')
