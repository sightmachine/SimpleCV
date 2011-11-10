import os
import sys
import tempfile
import urllib2
import warnings
import zipfile
import Tkinter
import simplejson as json


#Global Definitions
output_status = ""
cache_directory = ""
repo_url = ""
version_to_use = "1.2"
operating_system = None
app = None
current_file = None

def InstallButtonClick():
	"""
	This is the callback for the Install Button
	"""
	run()

def CancelButtonClick():
	"""
	This is the callback for the Cancel Button
	"""
	sys.exit()

def writeText(text):
	"""
	This is used to write to the UI console and terminal at the same time
	"""
	global output_status
	
	output_status.insert(Tkinter.END, text)
	output_status.insert(Tkinter.END, "\n")
	sys.stdout.write(text)
	sys.stdout.write("\n")

def download(URL):
	"""
	This downloads the file at the specified URL
	"""
	global cache_directory
	global operating_system
	global current_file
	
	if URL == None:
		warnings.warn("Please provide URL")
		return None

	tmpdir = cache_directory
	writeText("downloading")
	writeText(URL)
	filename = os.path.basename(URL)
	current_file = filename
	filepath = tmpdir + "\\" + filename
	if operating_system == "windows":
		path = tmpdir + "\\" + filename
	else:
		path = tmpdir + "/" + filename
		
	data = urllib2.urlopen(URL)
	chunk_read(data, report_hook=chunk_report)
	writeText("The file path is:")
	writeText(filepath)
	writeText("Saving file to disk please wait....")
	with open(filepath, "wb") as local_file:
		local_file.write(data.read())

	writeText(filename + " saved to disk")
	return (filepath, filename)


def extract(path):
	"""
	This extracts a zip file at the specfied system path
	"""
	tmpdir = cache_directory
	zfile = zipfile.ZipFile(path)
	writeText("Extracting zipfile")
	try:
		zfile.extractall(tmpdir)
	except:
		warnings.warn("Couldn't extract zip file")
		return None

	return tmpdir

def chunk_report(bytes_so_far, chunk_size, total_size):
	"""
	This is the update callback for the download
	"""
	global app
	global output_status
	global current_file
	
	percent = float(bytes_so_far) / total_size
	percent = round(percent*100, 2)
	writeText("Downloaded percent: " + str(percent) + "% of file: " + current_file)

	if bytes_so_far >= total_size:
		sys.stdout.write('\n')

	app.update()
	output_status.yview(Tkinter.END)
	
	
def chunk_read(response, chunk_size=8192, report_hook=None):
	"""
	This is for reading parts of the file in chunks for the download
	"""
	total_size = response.info().getheader('Content-Length').strip()
	total_size = int(total_size)
	bytes_so_far = 0

	while 1:
		chunk = response.read(chunk_size)
		bytes_so_far += len(chunk)

		if not chunk:
			break

		if report_hook:
			report_hook(bytes_so_far, chunk_size, total_size)

	return bytes_so_far

def run_install(path, name = "UNKNOWN"):
	"""
	This is used to run the installer at the specified path
	"""
	writeText("Running install for:" + name)
	writeText("on path: " + path)
	os.system(path)


def run():
	"""
	This runs the installation process
	"""
	writeText("Running the installer")
	cache_directory = tempfile.mkdtemp()
	filelist = json.load(open("manifest.json", "r"))
	urllist = filelist[version_to_use][operating_system]

	for url in urllist:
		path,name = download(url)
		run_install(path, name)



if __name__ == "__main__":

	if(len(sys.argv) > 1):
		repo_url = sys.argv[1]
	if(len(sys.argv) > 2):
		version_to_use = sys.argv[2]

	if(sys.platform.lower() == "linux2"):
		operating_system = "linux"
	else:
		operating_system = sys.platform.lower()
		
	header = "Welcome to the SimpleCV installer"
	instructions = "This installer will try to download and install all the libraries you need"
	instructions_cont = "please be patient while files download, if you are having problems visit:"
	website = "http://www.simplecv.org"

	app = Tkinter.Tk()
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
	w = Tkinter.Button(app, text="Install SimpleCV", command=InstallButtonClick)
	w.pack(side=Tkinter.RIGHT, padx=10, pady=10)
	w = Tkinter.Button(app, text="Cancel", command=CancelButtonClick)
	w.pack(side=Tkinter.RIGHT, padx=10, pady=10)

	scrollbar = Tkinter.Scrollbar(app)
	scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)

	output_status=Tkinter.Text(app,height=10,width=50,background='black', foreground='white', yscrollcommand=scrollbar.set)
	output_status.pack(side=Tkinter.BOTTOM)
	scrollbar.config(command=output_status.yview)
	output_status.insert(Tkinter.END, "Output Console\n")
	output_status.insert(Tkinter.END, "------------------------------\n")

	app.title('SimpleCV Installer - http://www.simplecv.org')
	app.mainloop()
