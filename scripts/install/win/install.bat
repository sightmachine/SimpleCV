@echo off
echo "Setting System paths"
SETX PATH C:/SimpleCV1.3/files/opencv/build/x86/vc10/bin/;C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.3/opencv/build/x86/vc10/bin/;%PATH%
SETX PYTHONPATH C:/SimpleCV1.3/files/opencv/build/python/2.7/;C:/OpenCV2.3/opencv/build/python/2.7/;%PYTHONPATH%
SET PATH=C:/SimpleCV1.3/files/opencv/build/x86/vc10/bin/;C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.3/opencv/build/x86/vc10/bin/;%PATH%
SET PYTHONPATH=C:/SimpleCV1.3/files/opencv/build/python/2.7/;C:/OpenCV2.3/opencv/build/python/2.7/;%PYTHONPATH%

echo "Running System Requirement Installers"
echo "Please click next on each of the additional installers"
echo "unless you don't need that specific library installed,"
echo "then click cancel on that specific installer"

cd "C:\SimpleCV1.3\files"
echo "Installing Python 2.7"
python-2.7.3.msi
echo "Installing Python Setuptools"
setuptools-0.6c11.win32-py2.7.exe
echo "Installing Scipy"
scipy-0.9.0rc5-win32-superpack-python2.7.exe
echo "Installing Numpy"
numpy-1.6.2-win32-superpack-python2.7.exe
echo "Install Pygame"
pygame-1.9.1.win32-py2.7.msi
echo "Installing OpenCV"
OpenCV-2.3.1-win-superpack.exe

easy_install pyreadline
easy_install PIL
easy_install cython
easy_install pip
pip install ipython
pip install https://github.com/ingenuitas/SimpleCV/zipball/1.3
echo "The Download path is:"
%1
mkdir C:\Python27\Lib\site-packages\freenect
echo "Copying freenect setup files"
xcopy %1\OpenKinect\precompiled\*.py C:\Python27\Lib\site-packages\freenect /y
xcopy %1\OpenKinect\precompiled\*.dll C:\Python27\DLLs /y
xcopy %1\OpenKinect\precompiled\*.pyd C:\Python27\DLLs /y
echo ""
echo "SimpleCV 1.3 is now installed"
echo ""
echo "This window will autoclose...."
timeout /T 10
