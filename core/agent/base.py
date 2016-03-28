# coding: utf-8

from fabkit import api

from oslo_config import cfg
from oslo_log import log
from oslo_service import service
from agent import AgentService
from central import CentralService
from manager import manage

CONF = cfg.CONF

LOG = log.getLogger(__name__)


@api.task
def agent():
    server = AgentService()
    lancher = service.launch(CONF, server, workers=1)
    lancher.wait()


@api.task
def agent_central():
    server = CentralService()
    lancher = service.launch(CONF, server, workers=1)
    lancher.wait()


@api.task
def agent_manager(*args, **kwargs):
    manage(*args, **kwargs)
