SimpleCV
=============

_a kinder, gentler machine vision framework_

SimpleCV is an interface for Open Source Machine Vision, using OpenCV and the Python programming language.    
It provides a consise, readable interface for cameras, image manipulation, feature extraction, and format conversion.  Our mission is to give casual users a comprehensive interface for basic machine vision functions and an elegant programming interface for advanced users.

We like SimpleCV because:

* Even beginning programmers can write simple machine vision tests
* Cameras, video files, images, and video streams are all interoperable
* Information on image features can be extracted, sorted and filtered easily
* Manipulations are fast, with easy to remember names
* Linear algebra is strictly optional

Here is the simplecv "hello world":

    from SimpleCV import Camera
    SimpleCV.Camera().getImage().save("picture.jpg")

For more code snippets, we recommend the [cookbook](http://simplecv.org/doc/cookbook.html) or looking at our example scripts in SimpleCV/examples

Installation
-------------------

If you haven't worked with OpenCV or Scipy before, your best bet is to get
one of our all-in-one Superpacks from SourceForge: http://sf.net/projects/simplecv/files/

You will absolutely need:

* OpenCV installed for your platform http://opencv.willowgarage.com/wiki/Instal
lGuide
* SciPY/Numpy installed for your platform http://www.scipy.org/Download
* Python Imaging Library is optional, but highly recommended http://www.pythonware.com/products/pil/

Once you have all the required libraries installed::

    easy_install simplecv

If you need more help, look at the installation docs: http://simplecv.org/doc/installation.html


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

SimpleCV Interactive Shell
---------------------------

Once you have SimpleCV installed, you can use it in a specialized iPython
shell.  This pre-loads all the symbols and gives you some extra functions
and macros for using SimpleCV.

To run the SimpleCV shell, from the installation directory type:

    python -m SimpleCV.__init__
    

