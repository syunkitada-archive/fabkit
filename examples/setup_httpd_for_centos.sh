#!/bin/sh -x

sudo yum install httpd mod_wsgi -y
sudo cp fabfile/examples/httpd_vhost.conf /etc/httpd/conf.d/
sudo mkdir -p /opt/fabkit/conf
sudo cp fabfile/examples/fabkit.wsgi /opt/fabkit/conf/
sudo mkdir -p /opt/fabkit/storage/log
sudo mkdir -p /opt/fabkit/storage/dump

if [ ! -e /opt/fabkit/fabfile ]; then
    if [ $# -e 1 -a $1 -e link ]; then
        sudo ln -s `pwd`/fabfile/ /opt/fabkit/fabfile
        sudo chmod 701 /home/`whoami`
    else
        sudo cp -r fabfile/ /opt/fabkit/fabfile
        sudo chown -R apache:apache /opt/fabkit
    fi
fi

sudo service httpd restart
sudo chkconfig httpd on
