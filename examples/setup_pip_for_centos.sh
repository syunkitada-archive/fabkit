#!/bin/sh -x

# install basic packages
sudo yum install python-devel libevent-devel libxml2-devel libxslt-devel -y

# remove packages that cause inconsistencies
sudo yum remove python-crypto -y

# Install pip for install fabric
if [ ! `which pip` ]; then
    pushd /tmp
    wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
    sudo easy_install pip
    popd
fi
