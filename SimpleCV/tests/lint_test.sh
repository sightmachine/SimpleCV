#!/bin/sh
pylint --reports=n --include-ids=y --disable=C0301,W0611,C0103,C0111,F0401,E0611,E1101 $1
