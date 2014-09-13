#!/bin/sh

# Install git
sudo yum install git


# Install pip for install fabric
sudo yum install python-devel libxml2-devel libxslt-devel
wget http://python-distribute.org/distribute_setup.py
sudo python distribute_setup.py
sudo easy_install pip

# Install fabric
sudo pip install fabric
