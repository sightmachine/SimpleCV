@echo off
SETX PATH C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.3/opencv/build/x86/vc10/bin/;%PATH%
SETX PYTHONPATH C:/OpenCV2.3/opencv/build/python/2.7/;%PYTHONPATH%
SET PATH=C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.3/opencv/build/x86/vc10/bin/;%PATH%
SET PYTHONPATH=C:/OpenCV2.3/opencv/build/python/2.7/;%PYTHONPATH%
cd "C:\SimpleCV1.3\files\"
python-2.7.3.msi
setuptools-0.6c11.win32-py2.7.exe
scipy-0.9.0rc5-win32-superpack-python2.7.exe
numpy-1.6.2-win32-superpack-python2.7.exe
pygame-1.9.1.win32-py2.7.msi
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
