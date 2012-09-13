How to build installer for windows
===============================================
The best method is to use a fresh copy of Windows in a virtual machine.

Once you have a virtual machine setup with a clean copy of windows, make
a snapshot of it because it will be useful for testing the installer
actually works.

VirtualBox was used for testing:
https://www.virtualbox.org


Setup the script files and required libraries.
-----------------------------------------------
Download all the required files listed in the README for SimpleCV on
windows and store all these files in a folder called 'files' on
the desktop of the Virtual Machine.

Also download the install.bat file and copy into this folder as well.

So for SimpleCV 1.3 we have:
Desktop/files/python-2.7.3.msi
Desktop/files/setuptools-0.6c11.win32-py2.7.exe
Desktop/files/scipy-0.9.0rc5-win32-superpack-python2.7.exe
Desktop/files/numpy-1.6.2-win32-superpack-python2.7.exe
Desktop/files/pygame-1.9.1.win32-py2.7.msi
Desktop/files/OpenCV-2.3.1-win-superpack.exe
Desktop/files/install.bat


Modify the install.bat file to include all the files you need to run post
installation. Make sure to update the system paths to match as well, for
instance we are using C:\SimpleCV1.3\files, make sure these all match up.
As well as the version of SimpleCV being installed by PIP.


Build the Installer
-----------------------------------------------
Download and Install the Advanced Installer for Windows:
http://www.advancedinstaller.com


* Create a Simple Project
* Fill out the project details tab
* Set to major upgrade when/if prompted instead of patch
* On the Install Parameters tab set the application folder to the correct version, in our case: c:\SimpleCV1.3
* On the files & folders tab, select the 'application folder', then add a folder from the top menu, and add our 'files' directory from the desktop
* On the dialog tab select 'ExitDialog', under the launch application section check the box 'launch application at the end of installation',
navigate to the desktop/files folder, you may have to select 'show all files' to see the install.bat file.
* Check the box, 'checked by default' and 'Run finish actions without displaying this dialog'.
* Now build the installer, it will prompt where to save the project, the desktop should be fine.

The installer should now be on the desktop in the folder 'SimpleCV1.3-SetupFiles'.

It is recommended that you snapshot the virtualmachine at this point to verify the installer works.
You will also have to copy the built setup installer from the VM before rolling back to the fresh install snapshot.



Note:  Please test the installer on a clean Virtual Machine before deploying.

