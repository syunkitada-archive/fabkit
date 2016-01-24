# coding: utf-8

from base import runserver  # noqa

runserver.__doc__ = """
Run fab server. this is not implement.

## Args
* [cluster_path/pattern],[find_depth]
  * load cluster and narrow down node from pattern.

## Examples
``` bash
# If use https, create certificate before run server
% fab runserver:create_cert

# Run server
% fab runserver
```
"""
