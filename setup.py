from setuptools import setup, find_packages
import os, sys, glob, fnmatch

setup(name="SimpleCV",
  version=1.3,
  download_url='https://github.com/sightmachine/SimpleCV/zipball/1.3',
  description="Make Computers See with SimpleCV, the Python Framework for Machine Vision",
  long_description="""Framework for computer (machine) vision in Python, providing a unified, pythonic interface to image acquisition, conversion, manipulation, and feature extraction.""",
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
  author='Sight Machine Inc',
  author_email='support@sightmachine.com',
  url='http://simplecv.org',
  license='BSD',
  packages = find_packages(exclude=['ez_setup']),
  zip_safe = False,
  requires=['cv2','cv', 'numpy', 'scipy', 'pygame', 'pil', 'svgwrite'],
  package_data  = { #DO NOT REMOVE, NEEDED TO LOAD INLINE FILES i = Image('simplecv')
            'SimpleCV': ['sampleimages/*',
                        'Features/HaarCascades/*',
                        'Features/FaceRecognizerData/*'
                        'examples/arduino/*',
                        'examples/detection/*',
                        'examples/display/*',
                        'examples/kinect/*',
                        'examples/machine-learning/*',
                        'examples/manipulation/*',
                        'examples/tracking/*'
                        ],
  },
  entry_points={
    'console_scripts': [
      'simplecv = SimpleCV.Shell:main',
    ],
  },

  )
