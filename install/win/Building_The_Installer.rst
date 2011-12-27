How to build installer for windows
===============================================
You need to download and install NSIS:
http://nsis.sourceforge.net/

Then put the:
EnvVarUpdate.nsh

In the NSIS install folder.  This is needed to set the system paths.

You then need to use NSIS to create a OpenKinect.exe from a Zip (If open
kinect has been updated)

Modify the install.bat file to include all the files you need to run post
installation.

Make sure you checkout the correct version of SimpleCV you want from git.
Then copy the SimpleCV folder to your desktop.  In that folder you can
remove the build, dist, as well as the hidden folder .git.

Then run NSIS and follow the wizard to build the setup file to create the
exe.  Once the setup file is generated update accordingly.

For instance you have to tell it to run install.bat when it is done, but
you may not be able to select it from the list in the wizard as it only
shows .exe files.   In our case we just picked the opencv.exe file
So after the install setup file is generated, you can
open it and manually set the section that says to launch the startup file
which was the opencv.exe we picked and change that to install.bat


Note:  Please test the installer on a clean Virtual Machine before deploying.

