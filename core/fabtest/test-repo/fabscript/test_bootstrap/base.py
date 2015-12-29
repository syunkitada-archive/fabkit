# cording: utf-8

from fabkit import task, Service, Package, filer, sudo


@task
def setup():
    Package('docker.io').install()

    filer.template(src='Dockerfile_centos7', dest='/tmp/Dockerfile_centos7')
    sudo('docker images | grep fab_centos7 ||'
         ' docker build -f /tmp/Dockerfile_centos7 -t fab_centos7 /tmp/')
    sudo('docker ps | grep fab_centos7 ||'
         ' docker run -i -d -p 40022:22 fab_centos7 /usr/sbin/sshd -D')

    filer.template(src='Dockerfile_ubuntu14', dest='/tmp/Dockerfile_ubuntu14')
    sudo('docker images | grep fab_ubuntu14 ||'
         ' docker build -f /tmp/Dockerfile_ubuntu14 -t fab_ubuntu14 /tmp/')
    sudo('docker run -i -d -p 40122:22 fab_ubuntu14 /usr/sbin/sshd -D')
