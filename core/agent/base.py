# coding: utf-8

from fabkit import api
import objects
import rpc

import oslo_messaging as messaging
from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service, periodic_task

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class TaskManager(periodic_task.PeriodicTasks):
    def __init__(self):
        super(TaskManager, self).__init__(CONF)
        self.service_name = 'agent'

    def periodic_tasks(self, context, raise_on_error=False):
        return self.run_periodic_tasks(context, raise_on_error=raise_on_error)

    @periodic_task.periodic_task(spacing=3)
    def hello(self, context):
        LOG.info('hello')
        print 'hello'


class AgentService(service.Service):

    def __init__(self):
        super(AgentService, self).__init__()
        self.manager = TaskManager()
        self.timers = []

    def start(self):
        LOG.info('start agent')

        target = messaging.Target(topic='fabric', server='localhost')

        endpoints = [
            self.manager,
            rpc.BaseRPCAPI(self.manager.service_name, self.backdoor_port)
        ]

        serializer = objects.FabObjectSerializer()

        self.rpcserver = rpc.get_server(target, endpoints, serializer)
        self.rpcserver.start()

        self.tg.add_dynamic_timer(self.periodic_tasks,
                                  initial_delay=0,
                                  periodic_interval_max=120)

    def periodic_tasks(self, raise_on_error=False):
        ctxt = {}
        return self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)

    def wait(self):
        LOG.info('wait agent')

    def stop(self):
        LOG.info('stop agent')

    def reset(self):
        LOG.info('reset agent')


@api.task
def agent():
    service.launch(CONF, AgentService(), workers=1).wait()
