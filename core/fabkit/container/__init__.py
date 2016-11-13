# noqa

from libvirt import Libvirt  # noqa
from docker import Docker  # noqa
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


def create(container):
    if container['provider'] == 'libvirt':
        libvirt = Libvirt(container)
        libvirt.create()

    return True


def delete(container):
    if container['provider'] == 'libvirt':
        libvirt = Libvirt(container)
        libvirt.delete()
