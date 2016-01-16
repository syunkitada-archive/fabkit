from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class FabService(service.ServiceBase):

    def start(self):
        pass

    def wait(self):
        pass

    def stop(self):
        pass

    def reset(self):
        pass
        # logging.setup(cfg.CONF, 'foo')
