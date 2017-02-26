# coding: utf-8

from base import test

test.__doc__ = """
Test fabkit or fablib.

## Args
* target, t
  * Set test target(all or module) to test fabfile.
* fablib, l
  * Set fablib target to test fablib.
* boostrap, b (default=true)
  * Whether run bootstrap task, before test.
* cluster, c (default=.*)
  * Filter cluster under test by regular expression.
* fabrun, f (default=.*)
  * Filter fabrun under test by regular expression.

## Examples
```
# test all module of fabkit
$ fab test:t=all

# test node module of fabkit
$ fab test:t=node

# test fablib/kubernetes.
$ fab test:l=kubernetes

# test fablib/openstack with no bootstrap.
$ fab test:l=openstack,b=false
```
"""
