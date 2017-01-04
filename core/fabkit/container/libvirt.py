# cording: utf-8

import random
import uuid
import time
from fabkit import filer, sudo, api, run
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
        # self.libvirt_dir = os.path.join(CONF._storage_dir, 'container', 'libvirt')
        self.libvirt_dir = os.path.join('/opt/fabkit', 'container', 'libvirt')
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.instances_dir = os.path.join(self.libvirt_dir, 'instances')
        filer.mkdir(self.instances_dir)

    def create(self):
        data = self.data
        sudo('modprobe kvm')
        sudo('modprobe kvm_intel')

        for i, vm in enumerate(data['libvirt_vms']):
            instance_dir = os.path.join(self.instances_dir, vm['name'])
            filer.mkdir(instance_dir)

            image_path = '{0}/vm.img'.format(instance_dir)
            vm['image_path'] = image_path
            src_image_path = self.wget_src_image(vm)
            if not filer.exists(image_path):
                sudo('cp {0} {1}'.format(src_image_path, image_path))
                sudo('qemu-img resize {0} {1}G'.format(image_path, vm.get('disk_size', 10)))

            configiso_path = self.create_configiso(vm, instance_dir)
            vm['configiso_path'] = configiso_path

            vm['mac'] = self.get_random_mac()

            domain_xml = self.create_domain_xml(vm, instance_dir)

            sudo("sed -i 's/^Defaults.*requiretty/# Defaults requiretty/' /etc/sudoers")

            sudo("virsh net-update default add ip-dhcp-host "
                 "\"<host mac='{0}' name='{1}' ip='{2}' />\"".format(
                     vm['mac'], vm['name'], vm['ip']))

            sudo('virsh define {0}'.format(domain_xml))
            sudo('chown -R root:root {0}'.format(instance_dir))
            sudo('virsh start {0}'.format(vm['name']))

        for vm in data['libvirt_vms']:
            while True:
                with api.warn_only():
                    if run('nmap -p 22 {0} | grep open'.format(vm['ip'])):
                        break
                    time.sleep(5)

        sudo("iptables -R FORWARD 1 -o virbr0 -s 0.0.0.0/0"
             " -d 192.168.122.0/255.255.255.0 -j ACCEPT")
        for vm in data['libvirt_vms']:
            for port in vm.get('ports', []):
                sudo("iptables -t nat -A PREROUTING -p tcp"
                     " --dport {0[1]} -j DNAT --to {1}:{0[0]}".format(
                         port, vm['ip']))

        for ip in data.get('iptables', {}):
            for port in ip.get('ports', []):
                sudo("iptables -t nat -A PREROUTING -p tcp"
                     " --dport {0[1]} -j DNAT --to {1}:{0[0]}".format(
                         port, ip['ip']))

        time.sleep(5)

    def delete(self):
        data = self.data
        for i, vm in enumerate(data['libvirt_vms']):
            with api.warn_only():
                sudo("virsh net-update default delete ip-dhcp-host \"`virsh net-dumpxml default"
                     " | grep '{0}' | sed -e 's/^ *//'`\"".format(vm['ip']))
                sudo('virsh list | grep {0} && virsh destroy {0}'.format(vm['name']))
                sudo('virsh list --all | grep {0} && virsh undefine {0}'.format(vm['name']))

            instance_dir = os.path.join(self.instances_dir, vm['name'])
            sudo('rm -rf {0}'.format(instance_dir))

    def stop(self):
        pass

    def start(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def wget_src_image(self, vm):
        images_dir = os.path.join(self.libvirt_dir, 'images')
        filer.mkdir(images_dir)

        src_image = vm['src_image'].rsplit('/', 1)[1]
        src_image_path = '{0}/{1}'.format(images_dir, src_image)
        src_image_format = 'qcow2'

        if src_image_path[-3:] == '.xz':
            src_image_path = src_image_path[:-3]
            src_image_format = 'xz'

        if not filer.exists(src_image_path):
            sudo('cd {0} && wget {1}'.format(images_dir, vm['src_image']))

            if src_image_format == 'xz':
                sudo('cd {0} && xz -d {1}'.format(images_dir, src_image))

        return src_image_path

    def create_configiso(self, vm, instance_dir):
        data = self.data

        template_data = {
            'user': CONF.job_user,
            'password': CONF.job_password,
            'vm': vm,
            'gateway': data['libvirt']['gateway'],
            'netmask': data['libvirt']['netmask'],
        }

        metadata_path = '{0}/meta-data'.format(instance_dir)
        userdata_path = '{0}/user-data'.format(instance_dir)
        configiso_path = '{0}/config.iso'.format(instance_dir)

        src_metadata_path = os.path.join(self.template_dir, 'meta-data')
        src_userdata_path = os.path.join(self.template_dir, vm['template'])
        filer.template(metadata_path, src_file=src_metadata_path, data=template_data)
        filer.template(userdata_path, src_file=src_userdata_path, data=template_data)
        if not filer.exists(configiso_path):
            sudo('genisoimage -o {0} -V cidata -r -J {1} {2}'.format(
                configiso_path, metadata_path, userdata_path))

        return configiso_path

    def create_domain_xml(self, vm, instance_dir):
        vm['uuid'] = str(uuid.uuid1())
        vm['tap'] = 'tap{0}'.format(vm['mac'].replace(':', ''))

        domain_xml = '{0}/domain.xml'.format(instance_dir)
        src_domain_xml = os.path.join(self.template_dir, 'domain.xml')
        filer.template(domain_xml, src_file=src_domain_xml, data=vm)
        return domain_xml

    def get_random_mac(self):
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]

        return ':'.join(map(lambda x: "%02x" % x, mac))
