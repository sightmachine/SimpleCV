from .base import *

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
      self.send_header('Content-type','text/html')
      self.end_headers()
      self.wfile.write("""
<html>
<head>
<style type=text/css>
  body { background-image: url(/stream); background-repeat:no-repeat; background-position:center top; background-attachment:fixed; background-size: 100% , auto; }
</style>
</head>
<body>
&nbsp;
</body>
</html>
      """)
    else:
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
            self.send_header("Content-type","image/jpeg")
            self.send_header("Content-Length", str(len(_jpegstreamers[port].jpgdata.getvalue())))
            self.end_headers()
            self.wfile.write(_jpegstreamers[port].jpgdata.getvalue() + "\r\n")
            lasttimeserved = time.time()
            print "posted frame " + str(count)
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
    elif (type(hostandport) == tuple):
      (self.host, self.port) = hostandport 

    self.sleeptime = st
    self.server = JpegTCPServer((self.host, self.port), JpegStreamHandler)
    self.server_thread = threading.Thread(target = self.server.serve_forever)
    _jpegstreamers[self.port] = self
    self.server_thread.daemon = True
    self.server_thread.start()
    self.framebuffer = self #self referential, ugh.  but gives some bkcompat



