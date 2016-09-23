# cording: utf-8

import random
import uuid
import time
import re
from fabkit import filer, sudo, api, env, run, cmd, sudo_cmd
from oslo_config import cfg
import os

CONF = cfg.CONF


class Libvirt():
    def __init__(self, container):
        self.data = container
        self.packages = {
            'Ubuntu 14.*': [
                'libvirt-bin',
                'qemu',
                'wget',
                'genisoimage',
            ],
            'CentOS Linux 7.*': [
                'epel-release',
                'libvirt',
                'virt-install',
                'qemu',
                'wget',
                'genisoimage',
            ],
        }
        self.services = [
            'libvirtd',
        ]

    def setup(self):
        data = self.data
        sudo_cmd('modprobe kvm')
        sudo_cmd('modprobe kvm_intel')

        for i, vm in enumerate(data['libvirt_vms']):
            template_data = {
                'user': CONF.test.user,
                'password': CONF.test.password,
                'vm': vm,
                'gateway': data['libvirt']['gateway'],
                'netmask': data['libvirt']['netmask'],
            }

            vm_dir = '/var/lib/libvirt/images/{0}'.format(vm['name'])
            image_path = '{0}/vm.img'.format(vm_dir)
            metadata_path = '{0}/meta-data'.format(vm_dir)
            userdata_path = '{0}/user-data'.format(vm_dir)
            configiso_path = '{0}/config.iso'.format(vm_dir)

            src_image = vm['src_image'].rsplit('/', 1)[1]
            src_image_path = '/var/lib/libvirt/images/{0}'.format(src_image)
            src_image_format = 'qcow2'

            if src_image_path[-3:] == '.xz':
                src_image_path = src_image_path[:-3]
                src_image_format = 'xz'

            if not os.path.exists(src_image_path):
                sudo_cmd('cd /var/lib/libvirt/images/ && wget {0}'.format(vm['src_image']))

                if src_image_format == 'xz':
                    sudo_cmd('cd /var/lib/libvirt/images/ && xz -d {0}'.format(src_image))

            with api.warn_only():
                sudo_cmd("virsh list --all | grep {0} && virsh destroy {0}"
                         " && virsh undefine {0}".format(vm['name']))

            sudo_cmd('rm -rf {0} && mkdir -p {0}'.format(vm_dir))

            if not os.path.exists(image_path):
                sudo_cmd('cp {0} {1}'.format(src_image_path, image_path))
                sudo_cmd('qemu-img resize {0} {1}G'.format(image_path, vm.get('disk_size', 10)))

            filer.template(metadata_path, src='meta-data', data=template_data)
            filer.template(userdata_path, src=vm['template'], data=template_data)
            if not os.path.exists(configiso_path):
                sudo_cmd('genisoimage -o {0} -V cidata -r -J {1} {2}'.format(
                    configiso_path, metadata_path, userdata_path))

            sudo_cmd("sed -i 's/^Defaults.*requiretty/# Defaults requiretty/' /etc/sudoers")

            vm['uuid'] = str(uuid.uuid1())
            vm['image_path'] = image_path
            vm['configiso_path'] = configiso_path
            vm['tap'] = 'tap{0}'.format(i)
            vm['mac'] = self.get_random_mac()
            domain_xml = '/tmp/domain-{0}.xml'.format(vm['name'])
            filer.template(domain_xml, src='domain.xml', data=vm)

            with api.warn_only():
                sudo_cmd("virsh net-update default delete ip-dhcp-host \"`virsh net-dumpxml default | grep '{0}' | sed -e 's/^ *//'`\"".format(vm['ip']))

            sudo_cmd("virsh net-update default add ip-dhcp-host "
                 "\"<host mac='{0}' name='{1}' ip='{2}' />\"".format(
                     vm['mac'], vm['name'], vm['ip']))

            sudo_cmd('virsh define {0}'.format(domain_xml))
            sudo_cmd('virsh start {0}'.format(vm['name']))

            # sudo("virt-install"
            #      " --connect=qemu:///system"
            #      " --name={name} --vcpus={vcpus} --ram={ram}"
            #      " --accelerate --hvm --virt-type=kvm"
            #      " --cpu host"
            #      " --network bridge=virbr0,model=virtio"
            #      " --disk {image_path},format=qcow2 --import"
            #      " --disk {configiso_path},device=cdrom"
            #      " --nographics &".format(
            #          name=vm['name'],
            #          vcpus=vm['vcpus'],
            #          ram=vm['ram'],
            #          image_path=image_path,
            #          configiso_path=configiso_path,
            #          ip=vm['ip'],
            #      ), pty=False)  # ), pty=False)

        for vm in data['libvirt_vms']:
            while True:
                with api.warn_only():
                    if run('nmap -p 22 {0} | grep open'.format(vm['ip'])):
                        break
                    time.sleep(5)

        sudo_cmd("iptables -R FORWARD 1 -o virbr0 -s 0.0.0.0/0"
                 " -d 192.168.122.0/255.255.255.0 -j ACCEPT")
        for vm in data['libvirt_vms']:
            for port in vm.get('ports', []):
                sudo_cmd("iptables -t nat -A PREROUTING -p tcp"
                         " --dport {0[1]} -j DNAT --to {1}:{0[0]}".format(
                             port, vm['ip']))

        for ip in data['iptables']:
            for port in ip.get('ports', []):
                sudo_cmd("iptables -t nat -A PREROUTING -p tcp"
                         " --dport {0[1]} -j DNAT --to {1}:{0[0]}".format(
                             port, ip['ip']))

    def start(self):
        pass

    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def get_random_mac(self):
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]

        return ':'.join(map(lambda x: "%02x" % x, mac))
