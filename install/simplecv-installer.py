import os
import sys
import tempfile
import urllib2
import warnings
import zipfile
import Tkinter

output_status = ""

def SaveButtonClick():
    run()

def CancelButtonClick():
    sys.exit()

def writeText(text):
    output_status.insert(Tkinter.END, text)
    output_status.insert(Tkinter.END, "\n")

def download(URL):
    if URL == None:
        warnings.warn("Please provide URL")
        return None

    tmpdir = tempfile.mkdtemp()
    filename = os.path.basename(URL)
    path = tmpdir + "\\" + filename
    data = urllib2.urlopen(URL)

    print("Saving file to disk please wait....")
    writeText("Saving file to disk please wait....")
    with open(path, "wb") as local_file:
        local_file.write(data.read())

    print filename + " saved to disk"
    return (path, filename)


def download_and_extract(URL):
    if URL == None:
        warnings.warn("Please provide URL")
        return None

    tmpdir = tempfile.mkdtemp()
    filename = os.path.basename(URL)
    path = tmpdir + "/" + filename
    zdata = urllib2.urlopen(URL)

    writeText("Saving file to disk please wait....")
    with open(path, "wb") as local_file:
        local_file.write(zdata.read())

    zfile = zipfile.ZipFile(path)    
    writeText("Extracting zipfile")
    try:
        zfile.extractall(tmpdir)
    except:
        warnings.warn("Couldn't extract zip file")
        return None

    return tmpdirw


def run_install(path, name = "UNKNOWN"):
    print("Running install for:" + name)
    print("on path: " + path)
    writeText("Running install for:" + name)
    writeText("on path: " + path)
    os.system(path)


def run():
    print "Running the installer"
    filelist = [
        "http://www.python.org/ftp/python/2.7.2/python-2.7.2.msi",
        "http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11.win32-py2.7.exe",
        "http://downloads.sourceforge.net/project/scipy/scipy/0.10.0rc1/scipy-0.10.0rc1-win32-superpack-python2.7.exe",
        "http://downloads.sourceforge.net/project/numpy/NumPy/1.6.1/numpy-1.6.1-win32-superpack-python2.7.exe",
        "http://archive.ipython.org/release/0.11/ipython-0.11.win32-setup.exe",
        "http://downloads.sourceforge.net/project/opencvlibrary/opencv-win/2.3.1/OpenCV-2.3.1-win-superpack.exe"
        ]

    for file in filelist:
        print "Running"
        print file
		writeText("Running")
		writeText(file)
		path,name = download(file)
		run_install(path, name)


if __name__ == "__main__":
    app = Tkinter.Tk()

    header = "Welcome to the SimpleCV installer"
    instructions = "This installer will try to download and install all the libraries you need"
    instructions_cont = "please be patient while files download, if you are having problems visit:"
    website = "http://www.simplecv.org"
    
    
    w = Tkinter.Label(app, text=header, font=("default",20))
    w.pack(padx=30, pady=20)
    w = Tkinter.Label(app, text="")
    w.pack()
    w = Tkinter.Label(app, text=instructions)
    w.pack()
    w = Tkinter.Label(app, text=instructions_cont)
    w.pack()
    w = Tkinter.Label(app, text=website)
    w.pack(pady=10)
    w = Tkinter.Button(app, text="Install SimpleCV", command=SaveButtonClick)
    w.pack(side=Tkinter.RIGHT, padx=10, pady=10)
    w = Tkinter.Button(app, text="Cancel", command=CancelButtonClick)
    w.pack(side=Tkinter.RIGHT, padx=10, pady=10)

    output_status=Tkinter.Text(app,height=10,width=50,background='black', foreground='white')
    output_status.pack(side=Tkinter.BOTTOM)
    output_status.insert(Tkinter.END, "Output Console\n")
    output_status.insert(Tkinter.END, "------------------------------\n")

    app.title('SimpleCV Installer - http://www.simplecv.org')
    app.mainloop()
