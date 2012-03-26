from setuptools import setup, find_packages
import sys, os

#from SimpleCV import __version__

setup(name="SimpleCV",
  version=1.2,
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
  packages = find_packages(exclude=['ez_setup', 'examples', 'tests', 'sampleimages']),
  zip_safe = True,

  requires=['cv2','cv', 'numpy', 'scipy', 'pygame', 'pil'],

  scripts=['scripts/simplecv']
  )
