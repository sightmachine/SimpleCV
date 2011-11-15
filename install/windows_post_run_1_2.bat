SETX PATH C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.2/bin/;%PATH%
SETX PYTHONPATH C:/OpenCV2.2/Python2.7/Lib/site-packages;%PYTHONPATH%
echo "Installing pyreadline"
easy_install pyreadline
echo "Installing PIL"
easy_install PIL
echo "Installing Cython"
easy_install cython
echo "Installing Nose"
easy_install nose
echo "Installing SimpleCV"
easy_install simplecv
SET DOWNLOAD_PATH = %1
mkdir C:\Python27\Lib\site-packages\freenect
echo "Copying freenect setup files"
xcopy %DOWNLOAD_PATH%\OpenKinect\precompiled\*.py C:\Python27\Lib\site-packages\freenect /y
xcopy %DOWNLOAD_PATH%\OpenKinect\precompiled\*.dll C:\Python27\DLLs /y
xcopy %DOWNLOAD_PATH%\OpenKinect\precompiled\*.pyd C:\Python27\DLLs /y
