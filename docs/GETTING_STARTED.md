# Getting Started

## Install Dependent Packages
If the following packages is already installed, skip this section.

### Dependent Packages
* git
* fabric
* chef
* knife-solo
* nife-solo_data_bag (option:recommendation)
* berkshelf (option:recommendation)
* chef-server (option:deprication)

### Install Dependent Packages
``` bash
# Install git
$ sudo yum install git


# Install pip for install fabric
$ sudo yum install python-devel libxml2-devel libxslt-devel
$ wget http://python-distribute.org/distribute_setup.py
$ sudo python distribute_setup.py
$ sudo easy_install pip

# Install fabric
$ sudo pip install fabric


# Install chef
$ curl -L https://www.opscode.com/chef/install.sh | sudo bash
$ sudo /opt/chef/embedded/bin/gem install knife-solo --no-ri --no-rdoc


# Install knife-solo
$ sudo /opt/chef/embedded/bin/gem install knife-solo --no-ri --no-rdoc


# Install knife-solo_data_bag (option:recommendation)
$ sudo /opt/chef/embedded/bin/gem install knife-solo_data_bag --no-ri --no-rdoc


# Install berkshelf (option:recommendation)
$ sudo /opt/chef/embedded/bin/gem install berkshelf --no-ri --no-rdoc
# Create symbolic link to /usr/local/bin to make it easy to use
$ sudo ln /opt/chef/embedded/bin/berks /usr/local/bin/berks


# Install chef-server (option:deprication)
# URL of rpm referred from opscode(http://www.getchef.com/chef/install/)
$ wget https://opscode-omnibus-packages.s3.amazonaws.com/el/6/x86_64/chef-server-11.0.12-1.el6.x86_64.rpm
$ sudo yum install chef-server-11.0.12-1.el6.x86_64.rpm
$ sudo chef-server-ctl reconfigure

# Check status of chef-server
$ sudo chef-server-ctl status
```

## Setup Chef Repository
### New Chef Repository
``` bash
# create new chef repository
$ knife solo init chef-repo
$ cd knife solo

# clone chefric
$ git clone https://github.com/syunkitada/chefric fabfile

# put the configuration file
$ cp fabfile/doc/fabfile.ini ./

# create localhost node(required)
$ fab node:create,localhost
[localhost] Executing task 'node'
['localhost']
Are you sure you want to create above nodes? (y/n) y
hostname(ipaddress)                               uptime         last_cook                run_list
--------------------------------------------------------------------------------------------------------
localhost()                                                      None                     []

Done.

$ cat nodes/localhost.json
{"name": "localhost", "run_list": []}
```

### Recommended Additional Configuration
* append .gitignore for ignore fabfile, *.pyc
  ``` bash
  $ cat chef-repo/.gitignore
  /cookbooks/
  /dev-cookbooks/
  
  .chef/*.pem
  .chef/data_bag_key
  
  /fabfile/
  *.pyc
  ```

## CONGRATULATIONS! COMPLETE SET UP!


