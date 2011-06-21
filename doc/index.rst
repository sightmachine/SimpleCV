.. SimpleCV documentation master file, created by
   sphinx-quickstart on Mon May 23 11:11:43 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SimpleCV: a kinder, gentler machine vision library 
======================================================

a kinder, gentler machine vision python library

SimpleCV is an interface for Open Source machine vision libraries in Python.   
It provides a consise, readable interface for cameras, image manipulation, feature extraction, and format conversion.  Our mission is to give casual users a comprehensive interface for basic machine vision functions and an elegant programming interface for advanced users.

Download from SourceForge: <http://sourceforge.net/projects/simplecv/files>

SourceForge Project Page: <http://sf.net/p/simplecv>



We like SimpleCV because:

 * Even beginning programmers can write simple machine vision tests
 * Cameras, video files, images, and video streams are all interoperable
 * Information on image features can be extracted, sorted and filtered easily
 * Manipulations are fast, with easy to remember names
 * Linear algebra is strictly optional


Here is the simplecv "hello world"::

    import SimpleCV

    c = SimpleCV.Camera()
    c.getImage().save("picture.jpg")

For more code snippets, look at the cookbook, or the example scripts.

Installation
---------------------------

You will absolutely need:

 * OpenCV installed for your platform http://opencv.willowgarage.com/wiki/InstallGuide
 * SciPY/Numpy installed for your platform http://www.scipy.org/Download

Once you have all the required libraries installed::

    easy_install simplecv

If you need more help, look at the `installation docs`<installation.html>


Required Libraries
----------------------

* OpenCV 2.2 with Python bindings http://opencv.willowgarage.com/wiki/
* SciPY http://www.scipy.org/

Optional Libraries
----------------------

* Python Image Library http://www.pythonware.com/products/pil/
* OpenKinect/freenect http://openkinect.org/wiki/Main_Page

Blob detection:

* CvBlob http://code.google.com/p/cvblob/
* cvblob-python https://github.com/oostendo/cvblob-python

Barcode reading:

* Zxing http://code.google.com/p/zxing/
* python-zxing https://github.com/oostendo/python-zxing

    
Contents
-----------------

.. toctree::
   :maxdepth: 2
   :glob:

   api
   installation
   cookbook


Videos
==================

`Nate demonstrating the Cookie Jar Alarm Example <http://www.youtube.com/watch?v=i5j3ORmaLTo>`_
`Anthony showing installation on Ubuntu Linux <http://www.youtube.com/watch?v=yiOkyVYbS8w>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

