#!/bin/sh

# Install git
sudo yum install git -y


# Install pip for install fabric
sudo yum install python-devel libxml2-devel libxslt-devel -y
wget http://python-distribute.org/distribute_setup.py
sudo python distribute_setup.py
rm -rf distribute*
sudo easy_install pip

# Install fabric
sudo pip install fabric


# init chefric repository and get chefric
git clone git@github.com:syunkitada/chefric.git fabfile
mkdir nodes
mkdir fablib
mkdir fabscript
touch fabscript/__init__.py
cp fabfile/examples/fabfile.ini ./


cat << EOF > ./.gitignore
/fablib/
/fabfile/

/cookbooks/
.chef/*.pem
.chef/data_bag_key

*.pyc
EOF
