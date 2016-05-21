# coding: utf-8

import time
import random
import datetime
import rpc
import service
import central
from oslo_service import periodic_task
from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils
import oslo_messaging as messaging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class AgentManager(periodic_task.PeriodicTasks):
    def __init__(self):
        super(AgentManager, self).__init__(CONF)
        self.service_name = 'agent'
        self.centralapi = central.CentralAPI()

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    @periodic_task.periodic_task(spacing=CONF.agent.agent_report_interval)
    def check(self, context):
        LOG.info('start check')

        agent_data = {
            'agent_type': 'agent',
            'host': CONF.host,
            'status': 'active',
            'setup_status': 0,
            'setup_timestamp': datetime.datetime.utcnow(),
            'check_status': 0,
            'check_timestamp': datetime.datetime.utcnow(),
            'fabscript_map': '{}',
        }

        self.centralapi.notify(agent_data)


class AgentRPCAPI(rpc.BaseRPCAPI):
    def __init__(self):
        target = messaging.Target(topic='agent', version='2.0', server=CONF.host)
        super(AgentRPCAPI, self).__init__('agent', target)

    def setup(self, context, arg):
        LOG.info('start setup')
        random_wait = arg.get('random_wait', 0)
        if random_wait > 0:
            wait_time = random.randint(0, random_wait)
            time.sleep(wait_time)

        resp = {
            'status': 0,
        }
        return jsonutils.to_primitive(resp)


class AgentAPI(rpc.BaseAPI):
    def __init__(self):
        target = messaging.Target(topic='agent', version='2.0', fanout=True)
        super(AgentAPI, self).__init__(target)

    def setup(self, arg={}, host=None):
        if host is None:
            return self.client.cast({}, 'setup', arg=arg)
        else:
            target = messaging.Target(topic='agent', version='2.0', server=CONF.host)
            transport = messaging.get_transport(CONF)
            client = messaging.RPCClient(transport, target)
            return client.call({}, 'setup', arg=arg)


class AgentService(service.Service):

    def __init__(self):
        super(AgentService, self).__init__(AgentManager(), AgentRPCAPI())
