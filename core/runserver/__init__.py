# coding: utf-8

from base import runserver  # noqa

runserver.__doc__ = """
Run web server.

## Args
* [cluster_path/pattern],[find_depth]
  * load cluster and narrow down node from pattern.

## Examples
``` bash
# If use https, create certificate before run server
% fab runserver:create_cert

# Run server
% fab runserver
[localhost] Executing task 'runserver'
(4148) wsgi starting up on http://0.0.0.0:8080/

# If you after login also run server
% nohup fab runserver &
```
"""
