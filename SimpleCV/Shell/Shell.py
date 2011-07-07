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
# http://sf.net/p/simplecv
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#load system libraries
from SimpleCV.__init__ import *
from subprocess import call
import platform

#Load simpleCV libraries
from SimpleCV.Shell.Tutorial import *
from SimpleCV.Shell.Help import *
from SimpleCV.Shell.Cheatsheet import *
from SimpleCV.Shell.Example import *

#libraries for the shell
from IPython.Shell import IPShellEmbed


#Command to clear the shell screen
def clear():
  if platform.system() == "Windows":
    return
  call("clear")

def magic_clear(self, arg):
  clear()

"""
If you run SimpleCV directly, it will launch an ipython shell
"""
def main():
    clear()
    banner = '+----------------------------------------------------+\n'
    banner += ' SimpleCV [interactive shell]\n'
    banner += '+----------------------------------------------------+\n'
    banner += '\n'
    banner += 'Commands: \n'
    banner += '\t"exit()" or press "Ctrl+ D" to exit the shell\n'
    banner += '\t"clear" to clear the shell screen\n'
    banner += '\t"tutorial" to begin the SimpleCV interactive tutorial\n'
    banner += '\t"cheatsheet" gives a cheatsheet of all the shell functions\n' 
    banner += '\t"simplehelp" gives list of commands or help on a certain command\n'
    banner += '\t"example" gives a list of examples you can run'
    banner += '\n'
    banner += 'Usage:\n'
    banner += '\tdot complete works to show library\n'
    banner += '\tfor example: Image().save("/tmp/test.jpg") will dot complete\n'
    banner += '\tjust by touching TAB after typing Image().\n'
    banner += '\n'
    banner += 'API Documentation:\n'
    banner += '\t"help function_name" will give in depth documentation of API\n'
    banner += '\t\texample:'
    banner += 'help Image or ?Image\n'
    banner += '\t\twill give the in-depth information about that class\n'
    banner += '\t"?function_name" will give the quick API documentation\n'
    banner += '\t\texample:'
    banner += '?Image.save\n'
    banner += '\t\twill give help on the image save function'

    

    
    exit_msg = '\nExiting the SimpleCV interactive shell\n'
    

    #setup terminal to show SCV prompt
    argsv = ['-pi1','SimpleCV:\\#>','-pi2','   .\\D.:','-po','SimpleCV:\\#>','-nosep']

    scvShell = IPShellEmbed(argsv)
    scvShell.set_banner(banner)
    scvShell.set_exit_msg(exit_msg)
    scvShell.IP.api.expose_magic("tutorial",magic_tutorial)
    scvShell.IP.api.expose_magic("clear", magic_clear)
    scvShell.IP.api.expose_magic("simplehelp", magic_help)
    scvShell.IP.api.expose_magic("cheatsheet", magic_cheatsheet)
    scvShell.IP.api.expose_magic("example", magic_examples)
    

    #Note that all loaded libraries are inherited in the embedded ipython shell
    sys.exit(scvShell())
