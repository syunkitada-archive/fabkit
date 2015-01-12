#!/bin/sh -x

sudo yum install httpd mod_wsgi -y
sudo cp fabfile/examples/httpd_vhost.conf /etc/httpd/conf.d/
sudo mkdir -p /opt/fabkit/conf
sudo cp fabfile/examples/fabkit.wsgi /opt/fabkit/conf/
sudo mkdir -p /opt/fabkit/log

if [ ! -e /opt/fabkit/webapp ]; then
    sudo ln -s `pwd`/fabfile/core/webapp /opt/fabkit/webapp
fi

sudo chmod 701 /home/`whoami`
sudo service httpd restart
sudo chkconfig httpd on
