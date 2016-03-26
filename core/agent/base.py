# coding: utf-8

from fabkit import api

from oslo_config import cfg
from oslo_log import log
from oslo_service import service
from agent import AgentService
from worker import WorkerService

CONF = cfg.CONF

LOG = log.getLogger(__name__)


@api.task
def agent():
    server = AgentService()
    lancher = service.launch(CONF, server, workers=1)
    lancher.wait()


@api.task
def worker():
    server = WorkerService()
    lancher = service.launch(CONF, server, workers=1)
    lancher.wait()
