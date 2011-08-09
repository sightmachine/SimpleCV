SET PATH=C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.2/bin/;%PATH%
SET PYTHONPATH=C:/OpenCV2.2/Python2.7/Lib/site-packages;%PYTHONPATH%
easy_install http://launchpad.net/pyreadline/trunk/1.7/+download/pyreadline-1.7.zip
easy_install Imaging-1.1.7
easy_install cython
easy_install nose-1.0.0
easy_install simplecv-git
mkdir C:\Python27\Lib\site-packages\freenect
xcopy .\OpenKinect\precompiled\*.py C:\Python27\Lib\site-packages\freenect /y
xcopy .\OpenKinect\precompiled\*.dll C:\Python27\DLLs /y
xcopy .\OpenKinect\precompiled\*.pyd C:\Python27\DLLs /y
