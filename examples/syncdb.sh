#!/bin/sh -x

pushd fabfile/core/webapp
./manage.py syncdb
popd
