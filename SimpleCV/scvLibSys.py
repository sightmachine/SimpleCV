#!/usr/bin/python

# SimpleCV system includes
import os, sys, warnings, time, socket, re, urllib2, types
import SocketServer
import threading
from copy import copy
from math import sqrt, atan2
from pkg_resources import load_entry_point
from SimpleHTTPServer import SimpleHTTPRequestHandler
from types import IntType, LongType, FloatType, InstanceType
from cStringIO import StringIO
from IPython.Shell import IPShellEmbed
