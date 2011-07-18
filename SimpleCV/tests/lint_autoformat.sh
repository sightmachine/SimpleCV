#!/bin/sh
# This regex auto indents lines
perl -pi -e ' s/^(\s+)/$1$1/; ' $1
# This regex adds spaces after line commas
perl -pi -e 's/\,(\S)/, $1/g' $1
