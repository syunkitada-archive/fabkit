#!/bin/sh -x

cd /tmp

sudo apt-get install wget gcc expect python-dev libevent-dev libxml2-dev libxslt-dev libffi-dev libssl-dev -y

wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
tar xvf Python-2.7.9.tgz
cd -
cd /tmp/Python-2.7.9
./configure --prefix=/opt/fabkit
make
sudo make altinstall
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo /opt/fabkit/bin/python2.7

cd -

sudo /opt/fabkit/bin/easy_install pip
sudo /opt/fabkit/bin/pip install -r ../requirements.txt
sudo ln -s /opt/fabkit/bin/fab /usr/bin/
