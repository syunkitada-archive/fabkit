#!/bin/sh

# Install git
sudo yum install git -y


# Install pip for install fabric
sudo yum install python-devel libxml2-devel libxslt-devel -y
wget http://python-distribute.org/distribute_setup.py
sudo python distribute_setup.py
sudo easy_install pip

# Install fabric
sudo pip install fabric


# init chefric repository and get chefric
git clone git@github.com:syunkitada/chefric.git fabfile
mkdir nodes
mkdir fablib
mkdir fabscript
cp examples/fabfile.ini ./