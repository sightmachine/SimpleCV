#!/bin/python
# This demo shows off using a web server and flash to upload and image
# and then do image processing in the cloud with SimpleCV then pass
# it back to the web browser via AJAX
#
# Using jpegcam as flash webcam library:
# http://code.google.com/p/jpegcam/
import os, tempfile, webbrowser, urllib, cherrypy, socket
from SimpleCV import *


class CloudCam(object):

    def index(self):
        f = urllib.urlopen("index.html") # load the default website
        s = f.read() # read the file
        f.close()
        return s
    index.exposed = True

    def upload(self):
        tmpfile = tempfile.NamedTemporaryFile(suffix=".png") #Make a temporary file
        tmpname = tmpfile.name.split("/")[-1] #grab the generated name
        filepath = os.getcwd() + "/" + tmpname #get the filepath
        outfile = open(filepath, 'w') # create the filestream to write output to
        outfile.write(cherrypy.serving.request.body.fp.read()) # read the raw data from the webserver and write to the temporary directory
        outfile.close() # close the temporary file
        self.process(filepath) #Use SimpleCV to process the image

        print "url:" + cherrypy.url()
        print "socket:" + socket.gethostbyname(socket.gethostname())
        #~ return "http://localhost:8000/" + tmpname #return the image path via ajax request
        return tmpname

    def process(self, filepath):
        img = Image(filepath) # load the image into SimpleCV
        img = img.edges() # Get the edges
        img.save(filepath) # save the temporary image
        return

    upload.exposed = True



if __name__ == '__main__':
    conf =  {'/':
                {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.getcwd()
                },
            'global' :
                {
                'server.socket_port': 8000,
                'server.socket_host' : '0.0.0.0'
                }
            }
    webbrowser.open("http://localhost:8000")
    cherrypy.quickstart(CloudCam(), config=conf)
