8/9/2011
kscottz

Hello SimpleCV Fans!

This readme will hold your hand in installing Freenect/Kinect support along with SimpleCV on Windows. The SimpleCV team tried to make this process as smooth as possible for Windows users by creating precompiled binaries for the freenect libraries. In laymens terms this means we took the raw ingredients for a Kinect pie and baked the pie for you. Currently these binaries are only for 32bit systems running Windows XP and Windows 7. 

*By default SimpleCV installs all of the needed binaries to run your Kinect, but you will still need to manually add the Kinect drivers to your system.*
 
---------------------------------------------------------------------
This is what freenect, the people who provide the kinect support, officially says to do:
From: http://openkinect.org/wiki/Getting_Started#Driver_installation

	There are two parts to libfreenect -- the low-level libusb-based device driver and libfreenect itself, the library that talks to the driver. You only need to install the driver once.
	
	Windows 7: step-by-step walkthrough (should also work with Windows XP!)
	Plug in your Kinect. Windows will warn that no device driver was found for the plugged device (the LED of Kinect will not turn on). If Windows presents a dialog asking to search for drivers, simply cancel it.
	
	Open the Device Manager: Start >> Control Panel >> System and Security >> System >> Device Manager

	A device called "Xbox NUI Motor" should be somewhere there (most probably be under "Other devices") with a small yellow warning symbol "!" on top of its icon. Right click on it, and select "Update Driver Software...", then click on "Browse my computer for driver software".
	
	"Browse" and select the folder where the "XBox_NUI_Motor.inf" is located (/platform/windows/inf inside your libfreenect source folder). Click "Next" and if warned by Windows that a non-certified driver is about to be installed, just order it to install it anyway.
	
	After that, the Kinect LED should start blinking green. Now there will be two additional devices in the Device Manager list: "Xbox NUI Camera" and "Xbox NUI Audio". Repeat the above instructions for them as well.
---------------------------------------------------------------------
We need to follow these directions too but we've put all of the drivers in a different place becasue we don't feel it is necessary to distribute the freenect source code. 
The exact same drivers should be found in the folder:

C:\Program Files\SimpleCV Superpack\OpenKinect\drivers

Other than the path the files and procedure should remain the same. 

To verify that the system has installed correctly you can try running:
C:\Program Files\SimpleCV Superpack\OpenKinect\freenect-examples\demo-tilt.py
-or-
C:\Program Files\SimpleCV Superpack\simplecv-git\SimpleCV\examples\kinect-coloring.py

*********************************************************************
We hope to have an on-line tutorial in a couple of days to help you out if you get stuck.
If you run into trouble you can just ping the team on Twitter at:

@sightmachine or @simple_cv

Or visit our forums:
http://help.simplecv.org

*********************************************************************
Have Fun

-kscottz
