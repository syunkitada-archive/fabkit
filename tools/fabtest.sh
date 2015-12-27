#!/bin/sh
#

coverage run `which fab` test
result=$?
coverage report

exit $result
