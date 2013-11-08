#!/usr/bin/python

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SimpleCV
# a kinder, gentler machine vision python library
#-----------------------------------------------------------------------
# SimpleCV is an interface for Open Source machine
# vision libraries in Python.
# It provides a concise, readable interface for cameras,
# image manipulation, feature extraction, and format conversion.
# Our mission is to give casual users a comprehensive interface
# for basic machine vision functions and an
# elegant programming interface for advanced users.
#
# more info:
# http://www.simplecv.org
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#load system libraries
from subprocess import call
import platform
import webbrowser
import sys

from SimpleCV.__init__ import *

#Load simpleCV libraries
from SimpleCV.Shell.Tutorial import *
from SimpleCV.Shell.Example import *

try:
    from SimpleCV import __version__ as SIMPLECV_VERSION
except ImportError:
    SIMPLECV_VERSION = ''


#Command to clear the shell screen
def shellclear():
    if platform.system() == "Windows":
        return
    call("clear")

#method to get magic_* methods working in bpython
def make_magic(method):
    def wrapper(*args, **kwargs):
        if not args:
            return method('', '')
        return method('', *args, **kwargs)

    return wrapper


def plot(arg):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("Matplotlib is not installed and required")
        return

    print "args", arg
    print "type", type(arg)
    plt.plot(arg)
    plt.show()


def hist(arg):
    try:
        import pylab
    except ImportError:
        logger.warning("pylab is not installed and required")
        return
    plot(pylab.hist(arg)[1])


def magic_clear(self, arg):
    shellclear()

def magic_forums(self, arg):
    webbrowser.open('http://help.simplecv.org/questions/')

def magic_walkthrough(self, arg):
    webbrowser.open('http://examples.simplecv.org/en/latest/')

def magic_docs(self, arg):
    webbrowser.open('http://www.simplecv.org/docs/')

banner = '+-----------------------------------------------------------+\n'
banner += ' SimpleCV '
banner += SIMPLECV_VERSION
banner += ' [interactive shell] - http://simplecv.org\n'
banner += '+-----------------------------------------------------------+\n'
banner += '\n'
banner += 'Commands: \n'
banner += '\t"exit()" or press "Ctrl+ D" to exit the shell\n'
banner += '\t"clear()" to clear the shell screen\n'
banner += '\t"tutorial()" to begin the SimpleCV interactive tutorial\n'
banner += '\t"example()" gives a list of examples you can run\n'
banner += '\t"forums()" will launch a web browser for the help forums\n'
banner += '\t"walkthrough()" will launch a web browser with a walkthrough\n'
banner += '\n'
banner += 'Usage:\n'
banner += '\tdot complete works to show library\n'
banner += '\tfor example: Image().save("/tmp/test.jpg") will dot complete\n'
banner += '\tjust by touching TAB after typing Image().\n'
banner += '\n'
banner += 'Documentation:\n'
banner += '\thelp(Image), ?Image, Image?, or Image()? all do the same\n'
banner += '\t"docs()" will launch webbrowser showing documentation'
banner += '\n'
exit_msg = '\n... [Exiting the SimpleCV interactive shell] ...\n'


def setup_ipython():
    try:
        import IPython
        from IPython.config.loader import Config
        from IPython.frontend.terminal.embed import InteractiveShellEmbed

        cfg = Config()
        cfg.PromptManager.in_template = "SimpleCV:\\#> "
        cfg.PromptManager.out_template = "SimpleCV:\\#: "
        #~ cfg.InteractiveShellEmbed.prompt_in1 = "SimpleCV:\\#> "
        #~ cfg.InteractiveShellEmbed.prompt_out="SimpleCV:\\#: "
        scvShell = InteractiveShellEmbed(config=cfg, banner1=banner,
                                         exit_msg=exit_msg)
        scvShell.define_magic("tutorial", magic_tutorial)
        scvShell.define_magic("clear", magic_clear)
        scvShell.define_magic("example", magic_examples)
        scvShell.define_magic("forums", magic_forums)
        scvShell.define_magic("walkthrough", magic_walkthrough)
        scvShell.define_magic("docs", magic_docs)
    except ImportError:
        try:
            from IPython.Shell import IPShellEmbed

            argsv = ['-pi1', 'SimpleCV:\\#>', '-pi2', '   .\\D.:', '-po',
                     'SimpleCV:\\#>', '-nosep']
            scvShell = IPShellEmbed(argsv)
            scvShell.set_banner(banner)
            scvShell.set_exit_msg(exit_msg)
            scvShell.IP.api.expose_magic("tutorial", magic_tutorial)
            scvShell.IP.api.expose_magic("clear", magic_clear)
            scvShell.IP.api.expose_magic("example", magic_examples)
            scvShell.IP.api.expose_magic("forums", magic_forums)
            scvShell.IP.api.expose_magic("walkthrough", magic_walkthrough)
            scvShell.IP.api.expose_magic("docs", magic_docs)
        except ImportError:
            raise

    return scvShell()


def setup_bpython():
    import bpython
    example = make_magic(magic_examples)
    clear = make_magic(magic_clear)
    docs = make_magic(magic_docs)
    tutorial = make_magic(magic_tutorial)
    walkthrough = make_magic(magic_walkthrough)
    forums = make_magic(magic_forums)
    temp = locals().copy()
    temp.update(globals())
    return bpython.embed(locals_=temp, banner=banner)


def setup_plain():
    import code

    return code.interact(banner=banner, local=globals())


def run_notebook(mainArgs):

    if IPython.__version__.startswith('1.'):
        """Run the ipython notebook server"""
        from IPython.html import notebookapp
        from IPython.html.services.kernels import kernelmanager
    else:
        from IPython.frontend.html.notebook import notebookapp
        from IPython.frontend.html.notebook import kernelmanager

    code = ""
    code += "from SimpleCV import *;"
    code += "init_options_handler.enable_notebook();"

    kernelmanager.MappingKernelManager.first_beat = 30.0
    app = notebookapp.NotebookApp.instance()
    mainArgs += [
        '--port', '5050',
        '--c', code,
    ]
    app.initialize(mainArgs)
    app.start()
    sys.exit()


def self_update():
    URL = "https://github.com/sightmachine/SimpleCV/zipball/master"
    command = "pip install -U %s" % URL

    if os.getuid() == 0:
        command = "sudo " + command

    returncode = call(command, shell=True)
    sys.exit()


def run_shell(shell=None):
    shells = ['setup_ipython', 'setup_bpython', 'setup_plain']
    available_shells = [shell] if shell else shells

    for shell in available_shells:
        try:
            return globals()[shell]()
        except ImportError:
            pass
    raise ImportError


def main(*args):
    log_level = logging.WARNING
    interface = None

    if len(sys.argv) > 1 and len(sys.argv[1]) > 1:
        flag = sys.argv[1]

        if flag == 'notebook':
            run_notebook(sys.argv[1:])
            sys.exit()

        elif flag == 'update':
            print "Updating SimpleCV....."
            self_update()

        if flag in ['--headless', 'headless']:
            # set SDL to use the dummy NULL video driver,
            #   so it doesn't need a windowing system.
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        elif flag in ['--nowarnings', 'nowarnings']:
            log_level = logging.INFO

        elif flag in ['--debug', 'debug']:
            log_level = logging.DEBUG

        if flag in ['--ipython', 'ipython']:
            interface = 'setup_ipython'

        elif flag in ['--bpython', 'bpython']:
            interface = 'setup_bpython'
        else:
            interface = 'setup_plain'

    init_logging(log_level)
    shellclear()
    scvShell = run_shell(interface)
