#!/usr/bin/python

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SimpleCV
# a kinder, gentler machine vision python library
#-----------------------------------------------------------------------
# SimpleCV is an interface for Open Source machine
# vision libraries in Python. 
# It provides a consise, readable interface for cameras,
# image manipulation, feature extraction, and format conversion.
# Our mission is to give casual users a comprehensive interface
# for basic machine vision functions and an
# elegant programming interface for advanced users.
#
# more info:
# http://www.simplecv.org
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#load system libraries
from SimpleCV.__init__ import *

from subprocess import call, Popen
import platform
import subprocess
import time

#Load simpleCV libraries
from SimpleCV.Shell.Tutorial import *
from SimpleCV.Shell.Cheatsheet import *
from SimpleCV.Shell.Example import *

IPVER = 0


#libraries for the shell

#if ipython version < 0.11
try:
  from IPython.Shell import IPShellEmbed
  IPVER = 10
except:
  try:
    import IPython
    from IPython.config.loader import Config
    from IPython.frontend.terminal.embed import InteractiveShellEmbed
    IPVER = 11
  except:
    raise("IPython is required to use the shell")


#Command to clear the shell screen
def shellclear():
  if platform.system() == "Windows":
    return
  call("clear")

def magic_clear(self, arg):
  shellclear()


def magic_editor(self, arg):

    os_type = platform.system().lower()
    print "please wait while checking for editor updates..."
    time.sleep(2)
    if os_type == "windows":
        print "Currently windows can't auto install the editor"
        print "this is a limitation of git on windows"
        return
        
    else:
        cmd = "git submodule update --init --recursive"
        call(["git","submodule","update","--init","--recursive"])
        path = "./SimpleCV/utils/cloud9/bin/cloud9.sh"


    
    #~ call(cmd) # update the editor

    print "...checking for updates complete"
    print "launching the editor"
    flags = "-w"
    args = "../../"
    Popen([path, flags, args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

"""
If you run SimpleCV directly, it will launch an ipython shell
"""

def setup_shell():
  
  banner = '+----------------------------------------------------+\n'
  banner += ' SimpleCV [interactive shell] - http://simplecv.org\n'
  banner += '+----------------------------------------------------+\n'
  banner += '\n'
  banner += 'Commands: \n'
  banner += '\t"exit()" or press "Ctrl+ D" to exit the shell\n'
  banner += '\t"clear" to clear the shell screen\n'
  banner += '\t"tutorial" to begin the SimpleCV interactive tutorial\n'
  banner += '\t"cheatsheet" gives a cheatsheet of all the shell functions\n' 
  banner += '\t"example" gives a list of examples you can run'
  banner += '\n'
  banner += 'Usage:\n'
  banner += '\tdot complete works to show library\n'
  banner += '\tfor example: Image().save("/tmp/test.jpg") will dot complete\n'
  banner += '\tjust by touching TAB after typing Image().\n'
  banner += 'API Documentation:\n'
  banner += '\t"help function_name" will give in depth documentation of API\n'
  banner += '\texample: help Image\n'
  banner += 'Editor:\n'
  banner += '\t"editor" will run the SimpleCV code editor in a browser\n'
  banner += '\t\texample:'
  banner += 'help Image or ?Image\n'
  banner += '\t\twill give the in-depth information about that class\n'
  banner += '\t"?function_name" will give the quick API documentation\n'
  banner += '\t\texample:'
  banner += '?Image.save\n'
  banner += '\t\twill give help on the image save function'
  exit_msg = '\n... [Exiting the SimpleCV interactive shell] ...\n'


  #IPython version is less than 11
  if IPVER <= 10:
    #setup terminal to show SCV prompt
    argsv = ['-pi1','SimpleCV:\\#>','-pi2','   .\\D.:','-po','SimpleCV:\\#>','-nosep']

    scvShell = IPShellEmbed(argsv)
    scvShell.set_banner(banner)
    scvShell.set_exit_msg(exit_msg)
    scvShell.IP.api.expose_magic("tutorial",magic_tutorial)
    scvShell.IP.api.expose_magic("clear", magic_clear)
    scvShell.IP.api.expose_magic("cheatsheet", magic_cheatsheet)
    scvShell.IP.api.expose_magic("example", magic_examples)
    scvShell.IP.api.expose_magic("editor", magic_editor)
    
    return scvShell

  #IPython version 0.11 or higher
  else:
    cfg = Config()
    cfg.InteractiveShellEmbed.PromptManager.in_template = "SimpleCV:\\#> "
    cfg.InteractiveShellEmbed.PromptManager.out_template = "SimpleCV:\\#: "
    scvShell = InteractiveShellEmbed(config=cfg, banner1=banner, exit_msg = exit_msg)
    scvShell.define_magic("tutorial",magic_tutorial)
    scvShell.define_magic("clear", magic_clear)
    scvShell.define_magic("cheatsheet", magic_cheatsheet)
    scvShell.define_magic("example", magic_examples)
    scvShell.define_magic("editor", magic_editor)

    return scvShell




def main():
    shellclear()
    
    scvShell = setup_shell()
    #Note that all loaded libraries are inherited in the embedded ipython shell
    sys.exit(scvShell())
