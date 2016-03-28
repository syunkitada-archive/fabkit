# coding: utf-8

from rpc import BaseRPCAPI, BaseAPI
from service import Service
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

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    @periodic_task.periodic_task(spacing=3)
    def hello(self, context):
        LOG.info('hello')
        print 'hello'


class AgentRPCAPI(BaseRPCAPI):
    def __init__(self):
        target = messaging.Target(topic='agent', version='2.0', server='server2')
        super(AgentRPCAPI, self).__init__('agent', target)

    def setup(self, context, arg):
        print 'fab client'
        resp = {
            'status': 0,
        }
        return jsonutils.to_primitive(resp)


class AgentAPI(BaseAPI):
    def __init__(self):
        target = messaging.Target(topic='agent', version='2.0', fanout=True)
        super(AgentAPI, self).__init__(target)

    def setup(self):
        return self.client.cast({}, 'setup', arg='')


class AgentService(Service):

    def __init__(self):
        super(AgentService, self).__init__(AgentManager(), AgentRPCAPI())