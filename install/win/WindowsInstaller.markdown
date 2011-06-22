**Building SimpleCV Windows Installer**

* You will need to download git and inno setup wizard: 
	http://www.jrsoftware.org/isdl.php

* Optionally you may also need to download this Inno plugin that allows you to interactively download components:
	http://www.sherlocksoftware.org/page.php?id=50

* I used IcoFx to generate icons:
	http://icofx.ro/

* The inno wizard script is called :
		simplecv_installer.iss

* The installer basically downloads all the dependencies and then just copies and installs the current, fixed version of the git repository. Downloads are broken into three parts:
	1. Major Libs (openCV, Python 2.7, easy_install) - we download and install these 
	2. Well supported libs (sci-py, num-py,ipytho) - we use a batch file called setup.bat to easy install these
	3. Not well supported libs (nose, cvblob,PIL) - we use the same batch file to install these from source

* To generate the installer put the following into a single directory. *Now is a good time to any Windows specific library changes*
		|
		|-simplecv-git (totally clean)
		|-Imaging-1.1.7 (PIL source)
		|-nose-1.0.0 (nose tests)
		|-setup.bat

* Modify setup.bat to install the correct versions of scipy, numpy and point to the correct directories etc. E.g. the batch file looks like this:

		SET PATH=C:\Python27\;%PATH%
		SET PATH=C:\Python27\Scripts;%PATH%
		SET PATH=C:\OpenCV2.2\bin%PATH%
		SET PYTHONPATH=C:/OpenCV2.2/Python2.7/Lib/site-packages;%PYTHONPATH%
		easy_install http://sourceforge.net/projects/numpy/files/NumPy/1.6.1rc1/numpy-1.6.1rc1-win32-superpack-python2.7.exe
		easy_install http://sourceforge.net/projects/scipy/files/scipy/0.9.0/scipy-0.9.0-win32-superpack-python2.7.exe
		easy_install http://ipython.scipy.org/dist/ipython-0.10.2.win32-setup.exe
		easy_install Imaging-1.1.7
		easy_install nose-1.0.0
		easy_install simplecv-git
		PAUSE

* Update the simplecv_installer.iss file to point to the source directory, i.e. 
		[Files]
		Source: "C:\SimpleCV\InstallSource\simplecv-git\SimpleCV\Shell\Shell.py"; DestDir: "{app}"; Flags: ignoreversion
		Source: "C:\SimpleCV\InstallSource\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
		; NOTE: Don't use "Flags: ignoreversion" on any shared system files

* Also update the downloads section to point to the correct http/ftp download locations. 
		itd_addfile('http://www.python.org/ftp/python/2.7.2/python-2.7.2.msi',expandconstant('{tmp}\python27.msi'));
		itd_addfile('http://downloads.sourceforge.net/project/opencvlibrary/opencv-win/2.2/OpenCV-2.2.0-win32-vs2010.exe',expandconstant('{tmp}\opencv.exe'));
		itd_addfile('http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11.win32-py2.7.exe',expandconstant('{tmp}\ezinstall.exe'))

* Run inno and everything should be baked into the exe file. 