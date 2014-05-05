# Getting Started

## Dependent Packages
* chef
* knife-solo
* nife-solo_data_bag (option:recommendation)
* berkshelf (option:recommendation)
* chef-server (option:deprication)

## Install Dependent Packages
``` bash
# Install chef
curl -L https://www.opscode.com/chef/install.sh | sudo bash
sudo /opt/chef/embedded/bin/gem install knife-solo --no-ri --no-rdoc


# Install knife-solo
sudo /opt/chef/embedded/bin/gem install knife-solo --no-ri --no-rdoc


# Install knife-solo_data_bag (option:recommendation)
sudo /opt/chef/embedded/bin/gem install knife-solo_data_bag --no-ri --no-rdoc


# Install berkshelf (option:recommendation)
sudo /opt/chef/embedded/bin/gem install berkshelf --no-ri --no-rdoc
# Create symbolic link to /usr/local/bin to make it easy to use
sudo ln /opt/chef/embedded/bin/berks /usr/local/bin/berks


# Install chef-server (option:deprication)
# URL of rpm referred from opscode(http://www.getchef.com/chef/install/)
wget https://opscode-omnibus-packages.s3.amazonaws.com/el/6/x86_64/chef-server-11.0.12-1.el6.x86_64.rpm
sudo yum install chef-server-11.0.12-1.el6.x86_64.rpm
sudo chef-server-ctl reconfigure

# Check status of chef-server
sudo chef-server-ctl status
```
