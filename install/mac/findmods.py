#!/usr/bin/python

from SimpleCV import *
import re
from types import NoneType

easy_installed_pkgs = dict() 
easy_installed_path = "/Library/Python/2.6/site-packages";

for k in sys.modules.keys():  
  if type(sys.modules[k]) == NoneType:
    continue

  fn = ""
  try:
    fn = sys.modules[k].__file__
  except:
    continue 
  
  if (re.match(easy_installed_path, fn)):
    junk, relpath = re.split(easy_installed_path, fn)
    dirs = re.split("/", relpath)
    easy_installed_pkgs[dirs[1]] = 1


for egg in easy_installed_pkgs.keys():
  print easy_installed_path + "/" + egg
