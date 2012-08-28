from paver.easy import *
from paver.setuputils import setup
from setuptools import find_packages

import paver.doctools
import paver.virtual
import paver.misctasks
from paved import *
from paved.dist import *
from paved.util import *
from paved.docs import *
from paved.pycheck import *
from paved.pkg import *
from sphinxcontrib import paverutils

# get info from setup.py
setup_py=''.join([x for x in path('setup.py').lines() if 'setuptools' not in x])
exec(setup_py)


options(
    sphinx=Bunch(
        docroot='docs',
        builddir="_build",
        ),
    pdf=Bunch(
        builddir='_build',
        builder='latex',
    ),
    )

options.paved.clean.rmdirs +=   ['.tox',
                                 'dist',
                                 'build' ,
                                 ]
options.paved.clean.patterns += ['*.pickle', 
                                 '*.doctree', 
                                 '*.gz' , 
                                 'nosetests.xml', 
                                 'sloccount.sc', 
                                 '*.pdf','*.tex', 
                                 '*.png',
                                 ]

options.paved.dist.manifest.include.remove('distribute_setup.py')
options.paved.dist.manifest.include.remove('paver-minilib.zip')
options.paved.dist.manifest.recursive_include.add('pyscreenshot *.conf')
options.paved.dist.manifest.include.add('requirements.txt')

@task
@needs(
#           'clean',
       'sloccount', 
       'html', 
       'pdf', 
       'sdist', 
       'nose',   'tox',
       )
def alltest():
    'all tasks to check'
    pass

@task
@needs('sphinxcontrib.paverutils.html')
def html():
    pass

@task
@needs('sphinxcontrib.paverutils.pdf')
def pdf():
    fpdf = list(path('docs/_build/latex').walkfiles('*.pdf'))[0]
    d=path('docs/_build/html')
    d.makedirs()
    fpdf.copy(d)

@task
def tox():
    '''Run tox.'''
    sh('tox')
    
@task
@needs('manifest', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our MANIFEST.in is generated.
    """
    pass
