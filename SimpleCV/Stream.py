from SimpleCV.base import *


_jpegstreamers = {}
class JpegStreamHandler(SimpleHTTPRequestHandler):
    """
    The JpegStreamHandler handles requests to the threaded HTTP server.
    Once initialized, any request to this port will receive a multipart/replace
    jpeg.   
    """


    def do_GET(self):
        global _jpegstreamers


        if (self.path == "/" or not self.path):


            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("""
<html>
<head>
<style type=text/css>
    body { background-image: url(/stream); background-repeat:no-repeat; background-position:center top; background-attachment:fixed; height:100% }
</style>
</head>
<body>
&nbsp;
</body>
</html>
            """)
            return 


        elif (self.path == "/stream"):
            self.send_response(200)
            self.send_header("Connection", "close")
            self.send_header("Max-Age", "0")
            self.send_header("Expires", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=--BOUNDARYSTRING")
            self.end_headers()
            (host, port) = self.server.socket.getsockname()[:2]
     
     
            count = 0
            timeout = 0.75 
            lasttimeserved = 0 
            while (1):
                if (_jpegstreamers[port].refreshtime > lasttimeserved or time.time() - timeout > lasttimeserved):
                    try:
                        self.wfile.write("--BOUNDARYSTRING\r\n")
                        self.send_header("Content-type", "image/jpeg")
                        self.send_header("Content-Length", str(len(_jpegstreamers[port].jpgdata.getvalue())))
                        self.end_headers()
                        self.wfile.write(_jpegstreamers[port].jpgdata.getvalue() + "\r\n")
                        lasttimeserved = time.time()
                    except socket.error, e:
                        return
                    except IOError, e:
                        return
                    count = count + 1 


                time.sleep(_jpegstreamers[port].sleeptime)




class JpegTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True


#factory class for jpegtcpservers
class JpegStreamer():
    """
    The JpegStreamer class allows the user to stream a jpeg encoded file
    to a HTTP port.  Any updates to the jpg file will automatically be pushed
    to the browser via multipart/replace content type.


    To initialize:
    js = JpegStreamer()


    to update:
    img.save(js)


    to open a browser and display:
    import webbrowser
    webbrowser.open(js.url)


    Note 3 optional parameters on the constructor:
    - port (default 8080) which sets the TCP port you need to connect to
    - sleep time (default 0.1) how often to update.  Above 1 second seems to cause dropped connections in Google chrome


    Once initialized, the buffer and sleeptime can be modified and will function properly -- port will not.
    """
    server = ""
    host = ""
    port = ""
    sleeptime = ""
    framebuffer = "" 
    counter = 0
    refreshtime = 0


    def __init__(self, hostandport = 8080, st=0.1 ):
        global _jpegstreamers
        if (type(hostandport) == int):
            self.port = hostandport
            self.host = "localhost"
        elif (type(hostandport) == str and re.search(":", hostandport)):
            (self.host, self.port) = hostandport.split(":")
            self.port = int(self.port)
        elif (type(hostandport) == tuple):
            (self.host, self.port) = hostandport 


        self.sleeptime = st
        self.server = JpegTCPServer((self.host, self.port), JpegStreamHandler)
        self.server_thread = threading.Thread(target = self.server.serve_forever)
        _jpegstreamers[self.port] = self
        self.server_thread.daemon = True
        self.server_thread.start()
        self.framebuffer = self #self referential, ugh.  but gives some bkcompat


    def url(self):
        """
        Returns the JpegStreams Webbrowser-appropriate URL, if not provided in the constructor, it defaults to "http://localhost:8080"
        """
        return "http://" + self.host + ":" + str(self.port) + "/"


    def streamUrl(self):
        """
        Returns the URL of the MJPEG stream. If host and port are not set in the constructor, defaults to "http://localhost:8080/stream/"
        """
        return self.url() + "stream"




class VideoStream():
    """
    The VideoStream lets you save video files in a number of different formats.


    You can initialize it by specifying the file you want to output::


        vs = VideoStream("hello.avi")
  
  
    You can also specify a framerate, and if you want to "fill" in missed frames. 
    So if you want to record a realtime video you may want to do this::


        vs = VideoStream("myvideo.avi", 25, True) #note these are default values


    Where if you want to do a stop-motion animation, you would want to turn fill off::


        vs_animation = VideoStream("cartoon.avi", 15, False) 
    
    
    If you select a fill, the VideoStream will do its best to stay close to "real time" by duplicating frames or dropping frames when the clock doesn't sync up
    with the file writes.


    You can save a frame to the video by using the Image.save() function::


        my_camera.getImage().save(vs)
    """


    fps = 25 
    filename = ""
    writer = ""
    fourcc = ""
    framefill = True
    videotime = 0.0
    starttime = 0.0
    framecount = 0
  
  
    def __init__(self, filename, fps = 25, framefill = True):
        (revextension, revname) = filename[::-1].split(".")
        extension = revextension[::-1]
        self.filename = filename
        self.fps = fps
        self.framefill = framefill 
        #if extension == "mpg":
        self.fourcc = cv.CV_FOURCC('I', 'Y', 'U', 'V')
            #self.fourcc = 0
        #else:
        #  warning.warn(extension + " is not supported for video writing on this platform, sorry");
        #  return False


    def initializeWriter(self, size):
        self.writer = cv.CreateVideoWriter(self.filename, self.fourcc, self.fps, size, 1)
        self.videotime = 0.0
        self.starttime = time.time()


    def writeFrame(self, img):
        """
        This writes a frame to the display object
        this is automatically called by image.save() but you can
        use this function to save just the bitmap as well so
        image markup is not implicit,typically you use image.save() but
        this allows for more finer control
        """
        if not self.writer:
            self.initializeWriter(img.size())
            self.lastframe = img


        frametime = 1.0 / float(self.fps)
        targettime = self.starttime + frametime * self.framecount 
        realtime = time.time()
        if self.framefill: 
            #see if we need to do anything to adjust to real time
            if (targettime > realtime + frametime):
                #if we're more than one frame ahead 
                #save the lastframe, but don't write to videoout
                self.lastframe = img
                return


            elif (targettime < realtime - frametime):
                #we're at least one frame behind
                framesbehind = int((realtime - targettime) * self.fps) + 1
                #figure out how many frames behind we are


                lastframes = framesbehind / 2
                for i in range(0, lastframes):
                    self.framecount += 1
                    cv.WriteFrame(self.writer, self.lastframe.getBitmap())


                theseframes = framesbehind - lastframes
                for i in range(0, theseframes):
                    self.framecount += 1
                    cv.WriteFrame(self.writer, img.getBitmap())
                #split missing frames evenly between the prior and current frame
            else: #we are on track
                self.framecount += 1
                cv.WriteFrame(self.writer, img.getBitmap())
        else:
            cv.WriteFrame(self.writer, img.getBitmap())
            self.framecount += 1
    
    
        self.lastframe = img




    
    
        
