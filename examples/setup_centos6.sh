#!/bin/sh -x

pushd /tmp

sudo yum install wget gcc gcc-gfortran python-devel libevent-devel libxml2-devel libxslt-devel libffi-devel openssl-devel blas-devel lapack-devel atlas-devel -y

wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
tar xvf Python-2.7.9.tgz
cd Python-2.7.9
./configure --prefix=/opt/fabkit
make
sudo make altinstall
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo /opt/fabkit/bin/python2.7

popd

sudo /opt/fabkit/bin/easy_install pip
sudo /opt/fabkit/bin/pip install -r ../requirements.txt
sudo ln -s /opt/fabkit/bin/fab /usr/bin/
