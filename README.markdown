SimpleCV
=============

_a kinder, gentler machine vision python library_

SimpleCV is an interface for Open Source machine vision libraries in Python.   
It provides a consise, readable interface for cameras, image manipulation, feature extraction, and format conversion.  Our mission is to give casual users a comprehensive interface for basic machine vision functions and an elegant programming interface for advanced users.

We like SimpleCV because:

* Even beginning programmers can write simple machine vision tests
* Cameras, video files, images, and video streams are all interoperable
* Information on image features can be extracted, sorted and filtered easily
* Manipulations are fast, with easy to remember names
* Linear algebra is strictly optional

Here is the simplecv "hello world":

    import SimpleCV

    c = SimpleCV.Camera()
    c.getImage().save("picture.jpg")

For more code snippets, we recommend the cookbook or looking at our example scripts

Installation
-------------------

You will absolutely need:

* OpenCV installed for your platform http://opencv.willowgarage.com/wiki/Instal
lGuide
* SciPY/Numpy installed for your platform http://www.scipy.org/Download
* Python Imaging Library is optional, but highly recommended http://www.pythonware.com/products/pil/

Once you have all the required libraries installed::

    easy_install simplecv

If you need more help, look at the installation docs


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

Installation
---------------------------

If you have all the required libraries installed::

    sudo python setup.py install

If you need more help, look at docs/installation.rst

Examples
---------------------------

Examples are in the SimpleCV/examples directory, you can also look at 
docs/cookbook.rst for reusable code snippets.


Running SimpleCV
---------------------------

To run SimpleCV, from the installation directory type:
python -m SimpleCV.__init__

This should launch the SimpleCV shell, if you are having problems
see http://www.simplecv.org for more help.



    

