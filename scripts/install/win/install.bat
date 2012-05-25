@echo off
SETX PATH C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.2/bin/;%PATH%
SETX PYTHONPATH C:/OpenCV2.2/Python2.7/Lib/site-packages;%PYTHONPATH%
SET PATH=C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.2/bin/;%PATH%
SET PYTHONPATH=C:/OpenCV2.2/Python2.7/Lib/site-packages;%PYTHONPATH%
cd "C:\Program Files\SimpleCV\install_files\"
python-2.7.2.msi
setuptools-0.6c11.win32-py2.7.exe
scipy-0.10.0rc1-win32-superpack-python2.7.exe
numpy-1.6.1-win32-superpack-python2.7.exe
ipython-0.10.2.win32-setup.exe
pygame-1.9.2a0.win32-py2.7.msi
OpenCV-2.2.0-win32-vs2010.exe

easy_install pyreadline
easy_install PIL
easy_install cython
easy_install nose
easy_install pip
pip install simplecv
echo "The Download path is:"
%1
mkdir C:\Python27\Lib\site-packages\freenect
echo "Copying freenect setup files"
xcopy %1\OpenKinect\precompiled\*.py C:\Python27\Lib\site-packages\freenect /y
xcopy %1\OpenKinect\precompiled\*.dll C:\Python27\DLLs /y
xcopy %1\OpenKinect\precompiled\*.pyd C:\Python27\DLLs /y
mklink c:%HOMEPATH%\Desktop\simplecv.py C:\Python27\Lib\site-packages\SimpleCV\__init__.py
