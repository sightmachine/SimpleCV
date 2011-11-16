SETX PATH C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.2/bin/;%PATH%
SETX PYTHONPATH C:/OpenCV2.2/Python2.7/Lib/site-packages;%PYTHONPATH%
SET PATH=C:/Python27/;C:/Python27/Scripts/;C:/OpenCV2.2/bin/;%PATH%
SET PYTHONPATH=C:/OpenCV2.2/Python2.7/Lib/site-packages;%PYTHONPATH%
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
