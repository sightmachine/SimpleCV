#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension
import re


def get_cython_version():
    """
    Returns:
        Version as a pair of ints (major, minor)

    Raises:
        ImportError: Can't load cython or find version
    """
    import Cython.Compiler.Main
    match = re.search('^([0-9]+)\.([0-9]+)',
                      Cython.Compiler.Main.Version.version)
    try:
        return map(int, match.groups())
    except AttributeError:
        raise ImportError

# Only use Cython if it is available, else just use the pre-generated files
try:
    cython_version = get_cython_version()
    # Requires Cython version 0.13 and up
    if cython_version[0] == 0 and cython_version[1] < 13:
        raise ImportError
    from Cython.Distutils import build_ext
    source_ext = '.pyx'
    cmdclass = {'build_ext': build_ext}
except ImportError:
    source_ext = '.c'
    cmdclass = {}


ext_modules = [Extension("freenect", ["freenect" + source_ext],
                         libraries=['usb-1.0', 'freenect', 'freenect_sync'],
                         runtime_library_dirs=[	'C:/Users/kscottz/Desktop/kinect/libusb-win32-bin-1.2.4.0/lib/msvc',
						 #'C:/Users/kscottz/Desktop/kinect/Pre-built.2/lib',
						 #
						 #'C:/Users/kscottz/Desktop/kinect/glut-3.7.6-bin',	'C:/Users/kscottz/Desktop/kinect/AugustBuild/libfreenect/build/lib/Release',
						 #'/usr/local/lib64',
                         #'/usr/lib/'
						 ],
                         extra_compile_args=[
						 '-I','C:/Users/kscottz/Desktop/kinect/AugustBuild/libfreenect/include',
						 '-I','C:/Users/kscottz/Desktop/kinect/libusb-win32-bin-1.2.4.0/include',
						 '-I','C:/Users/kscottz/Desktop/kinect/AugustBuild/libfreenect/platform/windows',
						 '-I','C:/Users/kscottz/Desktop/kinect/AugustBuild/libfreenect/platform/windows/libusb10emu',
						 '-I','C:/Users/kscottz/Desktop/kinect/AugustBuild/libfreenect/src',
						 '-I','C:/Python27/Lib/site-packages/numpy/core/include',
						 '-I','C:/Program Files/Microsoft Visual Studio 10.0/VC/include',
						 '-I', '../../include/',
						 '-I','C:/Users/kscottz/Desktop/kinect/AugustBuild/libfreenect/wrappers/c_sync'
                         ])]
setup(name='freenect',
      cmdclass=cmdclass,
      ext_modules=ext_modules)
