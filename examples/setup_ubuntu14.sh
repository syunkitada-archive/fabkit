#!/bin/sh -x

cd /tmp

sudo apt-get install wget gcc expect python-dev libevent-dev libxml2-dev libxslt-dev libffi-dev libssl-dev -y

if [ ! -e /opt/fabkit/bin/python2.7 ]; then
    wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
    tar xvf Python-2.7.9.tgz
    cd -
    cd /tmp/Python-2.7.9
    ./configure --prefix=/opt/fabkit
    make
    sudo make altinstall
    wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo /opt/fabkit/bin/python2.7

    sudo /opt/fabkit/bin/easy_install pip
fi

cd -
sudo /opt/fabkit/bin/pip install -r ../requirements.txt

if [ ! -e /usr/bin/fab ]; then
    sudo ln -s /opt/fabkit/bin/fab /usr/bin/
fi

if [ ! -e /usr/local/bin/node ]; then
    cd /tmp/
    wget https://nodejs.org/dist/v0.12.7/node-v0.12.7.tar.gz
    tar xvf node-v0.12.7.tar.gz
    cd -
    cd /tmp/node-v0.12.7
    ./configure
    make
    sudo make install
    cd -
fi

cd ../core/webapp/
sudo /usr/local/bin/npm install -g grunt-cli
/usr/local/bin/npm install
cd -
