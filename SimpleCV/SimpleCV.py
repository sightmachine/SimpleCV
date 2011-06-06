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
from scvLibSys import *
#library includes
from scvLibInc import *
#Load simpleCV optional libraries
from scvLibOptional import *
from subprocess import call

#Load simpleCV libraries
from scvImage import *
from scvCamera import *
from scvHelperFunctions import *
from scvDetection import *
from scvColor import *
from scvTutorial import *



#Globals
_cameras = [] 
_camera_polling_thread = ""
_jpegstreamers = {}

def clear():
  call("clear")

"""
If you run SimpleCV directly, it will launch an ipython shell
"""
if __name__ == '__main__':
  
    banner = '\n'
    banner += '+----------------------------------------------------+\n'
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
    banner += '\ttyping ? function name will give the API documentation\n'
    banner += '\tfor example: ?Image.save\n'
    banner += '\twill give help on the image save function and what is expected\n'
    

    
    exit_msg = '\nExiting the SimpleCV interactive shell\n'
    

    #setup terminal to show SCV prompt
    argsv = ['-pi1','SCV:>','-pi2','   .\\D.:','-po','SCV:>','-nosep']

    tutorial = Tutorial()
    scvShell = IPShellEmbed(argsv)
    scvShell.set_banner(banner)
    scvShell.set_exit_msg(exit_msg)

    #Note that all loaded libraries are inherited in the embedded ipython shell
    sys.exit(scvShell())
