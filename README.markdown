SimpleCV
=============

Make computers see with SimpleCV, the Open Source Framework for Vision

SimpleCV is an interface for Open Source Machine Vision, using OpenCV and the Python programming language.    
It provides a consise, readable interface for cameras, image manipulation, feature extraction, and format conversion.  Our mission is to give casual users a comprehensive interface for basic machine vision functions and an elegant programming interface for advanced users.

We like SimpleCV because:

* Even beginning programmers can write simple machine vision tests
* Cameras, video files, images, and video streams are all interoperable
* Information on image features can be extracted, sorted and filtered easily
* Manipulations are fast, with easy to remember names
* Linear algebra is strictly optional

Here is the simplecv "hello world":

    import SimpleCV
    SimpleCV.Camera().getImage().save("picture.jpg")

For more code snippets, we recommend the [cookbook](http://simplecv.org/doc/cookbook.html) or looking at our example scripts in SimpleCV/examples


---------------------------
Installation
---------------------------

If you haven't worked with OpenCV or Scipy before, your best bet is to get
one of our all-in-one Superpacks from SourceForge: http://sf.net/projects/simplecv/files/

You will absolutely need:

* OpenCV installed for your platform http://opencv.willowgarage.com/wiki/InstallGuide
* SciPY/Numpy installed for your platform http://www.scipy.org/Download
* Python Imaging Library http://www.pythonware.com/products/pil/
* PyGame for drawing and interfaces http://pygame.org

Once you have all the required libraries installed::

    easy_install simplecv

If you need more help, look at the installation docs: http://simplecv.org/doc/installation.html


`Easiest Method`

The easiest method to install SimpleCV is with the 1-click installers
located at <http://www.simplecv.org>.  These installers should
install all the necessary libraries you need to get SimpleCV up and
running easily.


`Easy Method`

If you need more specific instructions per platform there is:
<http://www.simplecv.org/doc/installation.html>

Optional Libraries
==================
Device Support:

* OpenKinect/freenect <http://openkinect.org/wiki/Main_Page>

Barcode reading:

* Zxing http://code.google.com/p/zxing/
* python-zxing https://github.com/oostendo/python-zxing

OCR:

* Tesseract http://code.google.com/p/tesseract-ocr/
* python-tesseract http://code.google.com/p/python-tesseract/

Machine Learning:

* Orange http://orange.biolab.si/ (with python bindings)

---------------------------    
Videos - Tutorials and Demos
---------------------------
Video tutorials and demos can be found at:
http://www.youtube.com/user/IngenuitasOfficial

or check out:
http://www.simplecv.org


---------------------------
SimpleCV Interactive Shell
---------------------------

Once you have SimpleCV installed, you can use it in a specialized iPython
shell.  This pre-loads all the symbols and gives you some extra functions
and macros for using SimpleCV.

To run the SimpleCV shell, from the installation directory type:

    python simplecv.py 
    

