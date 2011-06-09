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
from ..__init__ import *
from subprocess import call

#Load simpleCV libraries
from .Tutorial import *

#libraries for the shell
from IPython.Shell import IPShellEmbed

def clear():
  call("clear")

"""
If you run SimpleCV directly, it will launch an ipython shell
"""
def main():
    clear()

    banner = '+----------------------------------------------------+\n'
    banner += ' SimpleCV [interactive shell]\n'
    banner += '+----------------------------------------------------+\n'
    banner += '\n\n'
    banner += 'Commands: \n'
    banner += '\t"exit()" or press "Ctrl+ D" to exit the shell\n'
    banner += '\t"clear()" to clear the shell screen\n'
    banner += '\t"tutorial.start()" to begin the SimpleCV interactive tutorial\n'
    banner += '\n'
    banner += 'Usage:\n'
    banner += '\tdot complete works to show library\n'
    banner += '\tfor example: Image().save("/tmp/test.jpg") will dot complete\n'
    banner += '\tjust by touching TAB after typing Image().\n'
    banner += '\n'
    banner += 'Help:\n'
    banner += '\ttyping "help function_name" will give in depth documentation of API\n'
    banner += '\t\texample:'
    banner += 'help Image\n'
    banner += '\t\twill give the in-depth information about that class\n'
    banner += '\ttyping "?function_name" will give the quick API documentation\n'
    banner += '\t\texample:'
    banner += '?Image.save\n'
    banner += '\t\twill give help on the image save function'
    

    
    exit_msg = '\nExiting the SimpleCV interactive shell\n'
    

    #setup terminal to show SCV prompt
    argsv = ['-pi1','SimpleCV:\\#>','-pi2','   .\\D.:','-po','SimpleCV:\\#>','-nosep']

    tutorial = Tutorial()
    scvShell = IPShellEmbed(argsv)
    scvShell.set_banner(banner)
    scvShell.set_exit_msg(exit_msg)

    #Note that all loaded libraries are inherited in the embedded ipython shell
    sys.exit(scvShell())
