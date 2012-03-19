from setuptools import setup, find_packages
import sys, os

import os, sys, glob, fnmatch



## Added 10 Jan 2008
#~ from distutils.core import setup, Extension
#~ import distutils.command.install_data
#~ 
#~ ## Code borrowed from wxPython's setup and config files
#~ ## Thanks to Robin Dunn for the suggestion.
#~ ## I am not 100% sure what's going on, but it works!
#~ def opj(*args):
    #~ path = os.path.join(*args)
    #~ return os.path.normpath(path)
#~ 
#~ ## Added 10 Jan 2008
#~ # Specializations of some distutils command classes
#~ class wx_smart_install_data(distutils.command.install_data.install_data):
    #~ """need to change self.install_dir to the actual library dir"""
    #~ def run(self):
        #~ install_cmd = self.get_finalized_command('install')
        #~ self.install_dir = getattr(install_cmd, 'install_lib')
        #~ return distutils.command.install_data.install_data.run(self)
#~ 
#~ def find_data_files(srcdir, *wildcards, **kw):
    #~ # get a list of all files under the srcdir matching wildcards,
    #~ # returned in a format to be used for install_data
    #~ def walk_helper(arg, dirname, files):
        #~ if '.svn' in dirname:
            #~ return
        #~ names = []
        #~ lst, wildcards = arg
        #~ for wc in wildcards:
            #~ wc_name = opj(dirname, wc)
            #~ for f in files:
                #~ filename = opj(dirname, f)
#~ 
                #~ if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    #~ names.append(filename)
        #~ if names:
            #~ lst.append( (dirname, names ) )
#~ 
    #~ file_list = []
    #~ recursive = kw.get('recursive', True)
    #~ if recursive:
        #~ os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    #~ else:
        #~ walk_helper((file_list, wildcards),
                    #~ srcdir,
                    #~ [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    #~ return file_list
#~ 
#~ ## This is a list of files to install, and where:
#~ ## Make sure the MANIFEST.in file points to all the right 
#~ ## directories too.
#~ files = find_data_files('SimpleCV/', '*.*')
#~ 




from SimpleCV import __version__


setup(name="SimpleCV",
  version=__version__,
  download_url='http://sourceforge.net/projects/simplecv/files/1.2/SimpleCV-1.2.tar.gz',
  description="Make Computers See with SimpleCV, the Python Framework for Machine Vision",
  long_description="""Super-library for machine vision wrappers in Python, providing a unified, pythonic interface to image aquisition, conversion, manipulation, and feature extraction.""",
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Manufacturing',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
    'Topic :: Multimedia :: Graphics :: Graphics Conversion',
    'Topic :: Scientific/Engineering :: Image Recognition',
    'Topic :: Software Development :: Libraries :: Python Modules'],
  keywords='opencv, cv, machine vision, computer vision, image recognition, kinect, freenect',
  author='Ingenuitas Inc',
  author_email='support@ingenuitas.com',
  url='http://simplecv.org',
  license='BSD',
  packages = find_packages(exclude=['ez_setup']),
  zip_safe = True,
  requires=['cv', 'numpy', 'scipy', 'pygame', 'pil'],
  scripts=['scripts/simplecv'],
  package_data  = {
            'SimpleCV': ['sampleimages/*']
  }
  #~ data_files = files,
  )
