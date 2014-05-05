# Tutorial

## Hello World
``` bash
# creat cookbook "helloworld"
$ knife cookbook create helloworld -o site-cookbooks
** Creating cookbook helloworld
** Creating README for cookbook: helloworld
** Creating CHANGELOG for cookbook: helloworld
** Creating metadata for cookbook: helloworld

# edit recipe
$ echo 'log "helloworld"' >> site-cookbooks/helloworld/recipes/default.rb

# create node
$ fab node:create,192.168.254.131
[localhost] Executing task 'node'
['192.168.254.131']
Are you sure you want to create above nodes? (y/n) y
hostname(ipaddress)                               uptime         last_cook                run_list
--------------------------------------------------------------------------------------------------------
192.168.254.131()                                                None                     []

# edit node to change run_list
$ fab node:edit,192.168.254.131,run_list,recipe[helloworld]
[localhost] Executing task 'node'
hostname(ipaddress)                               uptime         last_cook                run_list
--------------------------------------------------------------------------------------------------------
192.168.254.131()                                                None                     []


Edit above nodes.
hostname(ipaddress)                               uptime         last_cook                run_list
--------------------------------------------------------------------------------------------------------
192.168.254.131()                                                None                     recipe[helloworld]

Done.


# install chef to node if not installed chef
$ fab node:*131 prepare
[localhost] Executing task 'node'
hostname(ipaddress)                               uptime         last_cook                run_list
--------------------------------------------------------------------------------------------------------
192.168.254.131()                                 16:46          prepared                 recipe[helloworld]
Are you sure you want to run task that follow on above nodes? (y/n) y
enter your password

[localhost] sudo: hostname
[localhost] out: sudo password: <enter your password>


# run chef-solo on node
$ fab node:*131 cook
[localhost] Executing task 'node'
hostname(ipaddress)                               uptime         last_cook                run_list
--------------------------------------------------------------------------------------------------------
192.168.254.131()                                 16:46          prepared                 recipe[helloworld]
Are you sure you want to run task that follow on above nodes? (y/n) y
enter your password

[localhost] sudo: hostname
[localhost] out: sudo password: <enter your password>

...

[192.168.254.131] out: Starting Chef Client, version 11.12.2
[192.168.254.131] out: Compiling Cookbooks...
[192.168.254.131] out: Converging 1 resources
[192.168.254.131] out: Recipe: helloworld::default
[192.168.254.131] out:   * log[helloworld] action write
[192.168.254.131] out:
[192.168.254.131] out:
[192.168.254.131] out: Running handlers:
[192.168.254.131] out: Running handlers complete


# show node list
$ fab node:*
[localhost] Executing task 'node'
hostname(ipaddress)                               uptime         last_cook                run_list
--------------------------------------------------------------------------------------------------------
localhost()                                                                               recipe[]
192.168.254.131()                                 17:03          2014-05-04 04:58:51[0]   recipe[helloworld]
```

