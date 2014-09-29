#!/bin/sh -x

# Install git
sudo yum install git -y

sudo yum install python-devel libevent-devel libxml2-devel libxslt-devel -y

pushd /tmp
# Install pip for install fabric

which pip
if [ $? != 0 ]; then
    wget https://pypi.python.org/packages/source/d/distribute/distribute-0.6.49.tar.gz
    tar -xvf distribute-0.6.49.tar.gz
    pushd distribute-0.6.49
    sudo python setup.py install
    sudo easy_install pip
    popd
    sudo rm -rf distribute*
fi

popd

# Install fabric
sudo yum remove python-crypto
sudo pip install fabric


# init chefric repository and get chefric
# git clone git@github.com:syunkitada/chefric.git fabfile
# mkdir nodes
# mkdir fablib
# mkdir fabscript
# touch fabscript/__init__.py
# cp fabfile/examples/fabfile.ini ./


# cat << EOF > ./.gitignore
# /fablib/
# /fabfile/
# 
# /cookbooks/
# .chef/*.pem
# .chef/data_bag_key
# 
# *.pyc
# EOF
