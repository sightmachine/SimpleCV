from setuptools import setup, find_packages
import sys, os

setup(name="SimpleCV",
  version="0.9",
  description="A kinder, gentler Python Vision Library",
  long_description="""Super-library for machine vision wrappers in Python, providing a unified, pythonic interface to image aquisition, conversion, manipulation, and feature extraction.""",
  classifiers=[
    'Development Status :: 4 - Beta',
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
  requires=['cv', 'numpy', 'scipy', 'scipy.spatial.distance']
  )
