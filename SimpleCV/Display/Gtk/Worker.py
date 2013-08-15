from multiprocessing import Process,Pipe
import os
from ..Base import Display
from ..Base import Display
from ..Base import Line,Circle,Rectangle,Polygon,Ellipse,Bezier,Text
from ..Base.Display import *
import numpy as np
from ... import Image
import math
import cairo
from ...Color import Color

def drawShape(cr,shape):
    """
    
    **SUMMARY**
    
    Draws a shape on the image
    

    **PARAMETERS**
    
    * *cr* - The cairo context to draw on
    
    * *shape* - The shape to draw
    
    """
    r,g,b = shape.color
    r,g,b = float(r)/255,float(g)/255,float(b)/255
    a = float(shape.alpha)/255
    cr.set_source_rgba(r,g,b,a)
    cr.set_antialias(cairo.ANTIALIAS_DEFAULT if shape.antialias else cairo.ANTIALIAS_NONE)
    if(type(shape) == Line):
        cr.set_line_width(shape.width)
        cr.move_to(*shape.start)
        cr.line_to(*shape.stop)
        cr.stroke()
    elif(type(shape) == Circle):
        cr.set_line_width(shape.width)
        cr.arc(shape.center[0],shape.center[1], shape.radius, 0., 2 * math.pi)
        cr.stroke_preserve()
        if shape.filled:
            cr.fill()
        else:
            cr.stroke()
    elif(type(shape) == Rectangle):
        cr.set_line_width(shape.width)
        w = shape.pt2[0]-shape.pt1[0]
        h = shape.pt2[1]-shape.pt1[1]
        cr.rectangle(shape.pt1[0],shape.pt1[1],w,h)
        cr.stroke_preserve()
        if shape.filled:
            cr.fill()
        else:
            cr.stroke()
    elif(type(shape) == Text):
    
        slant = cairo.FONT_SLANT_ITALIC if shape.italic else cairo.FONT_SLANT_NORMAL
        weight = cairo.FONT_WEIGHT_BOLD if shape.bold else cairo.FONT_WEIGHT_NORMAL
        cr.select_font_face(shape.font,slant,weight)
        cr.set_font_size(shape.size)
        x,y,w,h, = cr.text_extents(shape.text)[:4]
    
        if(shape.bg):
            #drawing the text background
            cr.rectangle(shape.location[0]+x,shape.location[1]+y,w,h)
            r,g,b = shape.bg
            r,g,b = float(r)/255,float(g)/255,float(b)/255
            a = float(shape.alpha)/255
            cr.set_source_rgba(r,g,b,a)
            cr.fill()
            r,g,b = shape.color
            
        r,g,b = shape.color
        r,g,b = float(r)/255,float(g)/255,float(b)/255
        a = float(shape.alpha)/255
        cr.set_source_rgba(r,g,b,a)
        
        cr.move_to(*shape.location)
        cr.show_text(shape.text)
        cr.stroke()

    elif(type(shape) == Polygon):
        cr.set_line_width(shape.width)
        cr.move_to(*shape.points[-1])
        for point in shape.points:
            cr.line_to(*point)
        cr.close_path()
        if shape.filled:
            cr.fill()
        else:
            cr.stroke()
    elif(type(shape) == Ellipse):
        cr.set_line_width(shape.width)
        cr.save()
        cr.translate(shape.center[0]+shape.dimensions[0]/2.,shape.center[1]+shape.dimensions[1]/2.)
        cr.scale(shape.dimensions[0]/float(shape.dimensions[1]), 1.)
        cr.arc(0,0, shape.dimensions[1], 0., 2 * math.pi)
        cr.restore()
        if shape.filled:
            cr.fill()
        else:
            cr.stroke()
    elif(type(shape) == Bezier):
        points = shape.points
        cr.set_line_width(shape.width)
        cr.curve_to(points[0][0],points[0][1],points[1][0],points[1][1],points[2][0],points[2][1],)
        cr.stroke()


#returns x,y,xScale,yScale
#copied from adaptiveScale in ImageClass
def smartScale(gdk, src, resolution):
    """
    **SUMMARY**
    
    Resizes an image preserving its aspect ratio. Copied from adaptive scale.
    Is used to resize image for the display
    
    **PARAMETERS**
    
    * *gdk* - A gdk module object
    
    * *src* - The source pixbuf ( gtk.gdk.pixbuf )
    
    * *resolution*  - The desired resouution to scale to.
    
    **RETURNS**
    
    A resized pixbuf.
    
    """
    srcWidth = src.get_width()
    srcHeight = src.get_height()
    srcSize = srcWidth,srcHeight

    wndwAR = float(resolution[0])/float(resolution[1])
    imgAR = float(srcWidth)/float(srcHeight)

    targetx = 0
    targety = 0
    targetw = resolution[0]
    targeth = resolution[1]

    if( srcSize == resolution): # we have to resize
        return src
    elif( imgAR == wndwAR ):
        wScale = float(resolution[0])/srcWidth
        hScale = float(resolution[1])/srcHeight 
        return src.scale_simple(resolution[0],resolution[1],gdk.INTERP_BILINEAR)
    else:
        #scale factors

        wscale = (float(srcWidth)/float(resolution[0]))
        hscale = (float(srcHeight)/float(resolution[1]))
        if(wscale>1): #we're shrinking what is the percent reduction
            wscale=1-(1.0/wscale)
        else: # we need to grow the image by a percentage
            wscale = 1.0-wscale
        if(hscale>1):
            hscale=1-(1.0/hscale)
        else:
            hscale=1.0-hscale
        if( wscale == 0 ): #if we can get away with not scaling do that
            targetx = 0
            targety = (resolution[1]-srcHeight)/2
            targetw = srcWidth
            targeth = srcHeight
        elif( hscale == 0 ): #if we can get away with not scaling do that
            targetx = (resolution[0]-srcWidth)/2
            targety = 0
            targetw = srcWidth
            targeth = srcHeight
        elif(wscale < hscale): # the width has less distortion
            sfactor = float(resolution[0])/float(srcWidth)
            targetw = int(float(srcWidth)*sfactor)
            targeth = int(float(srcHeight)*sfactor)
            if( targetw > resolution[0] or targeth > resolution[1]):
                #aw shucks that still didn't work do the other way instead
                sfactor = float(resolution[1])/float(srcHeight)
                targetw = int(float(srcWidth)*sfactor)
                targeth = int(float(srcHeight)*sfactor)
                targetx = (resolution[0]-targetw)/2
                targety = 0
            else:
                targetx = 0
                targety = (resolution[1]-targeth)/2

        else: #the height has more distortion
            sfactor = float(resolution[1])/float(srcHeight)
            targetw = int(float(srcWidth)*sfactor)
            targeth = int(float(srcHeight)*sfactor)
            if( targetw > resolution[0] or targeth > resolution[1]):
                #aw shucks that still didn't work do the other way instead
                sfactor = float(resolution[0])/float(srcWidth)
                targetw = int(float(srcWidth)*sfactor)
                targeth = int(float(srcHeight)*sfactor)
                targetx = 0
                targety = (resolution[1]-targeth)/2
            else:
                targetx = (resolution[0]-targetw)/2

    return src.scale_simple(targetw,targeth,gdk.INTERP_BILINEAR)


class GtkWorker(Process):
    """
    A Process for handling a single Display window. Each GtkDisplay window has
    one instance of this class. For each task the GtkDisplay sends a message
    to it's GtkWorker.All communicattion happens over a duplex pipe.
    
    Each GUI function (*) in GtkDisplay has a corresponding handle_* method in
    GtkWorker . 
    
    eg. GtkDisplay.showImage() corresponds to GtkWorker.handle_showImage()
    
    
    """
    
    #the glade file contatning the gtk GUI layout
    _gladeFile = "main.glade"
    BGCOLOR = (0,0,0)
    def __init__(self,connection,size,type_,title,fit):
        """
        **SUMMARY**
        
        Creates a new process to handle the gtk mainloop for a display.
        
        **PARAMETERS**
        
        * *connection* - The connection used to communicate with parent
         
        * *size* - Initial size of display.
        
        * *type_* - The type of dispay.
        
        * *fit* - the fitting methods of the display.
        
        """
        #TODO , the doc references
        Process.__init__(self)
        self.connection = connection
        self.size = size
        self.fit = fit
        self.title = title
        self.type_ = type_
        self.daemon = True

    def run(self):
        """
        **SUMMARY**
        
        Loads the layout from the glade file and starts the gtk mainloop
        
        """
        #Gtk imports have to be done in run, Otherwise Gtk thknks there are
        #multiple copies of itself. These will be local to each process
        import gtk
        import gobject
        self.gtk = gtk
        
        
        #Loads the GUI from file and connects signals
        builder = gtk.Builder()
        path = os.path.dirname(__file__) + os.sep + GtkWorker._gladeFile
        builder.add_from_file(path)
        builder.connect_signals(self)
        
        #get required wigdets
        self.window = builder.get_object("window")
        self.scrolledWindow = builder.get_object("scrolledWindow")
        self.drawingArea = gtk.DrawingArea()
        self.builderWindow = builder.get_object("builderWindow")
        self.applyListStore = builder.get_object("applyListStore")
        self.filterListStore = builder.get_object("filterListStore")
        self.filterTreeview = builder.get_object("filterTreeview")
        self.applyTreeview = builder.get_object("applyTreeview")

        #Masks are added to get mouse button press, release and mouse pointer motion events
        self.drawingArea.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.BUTTON_RELEASE_MASK|gtk.gdk.POINTER_MOTION_MASK)

        #glade doesnt seem to have expose-event
        self.drawingArea.connect("expose-event",self.draw)

        #connecting mouse events related signals to functions
        self.drawingArea.connect("button_press_event",self.mouse_press)
        self.drawingArea.connect("button_release_event",self.mouse_release)
        self.drawingArea.connect("scroll_event",self.mouse_scroll)
        self.drawingArea.connect("motion_notify_event", self.mouse_motion)
        
        
        
        self.scrolledWindow.add_with_viewport(self.drawingArea)
        self.viewPort = self.scrolledWindow.children()[0]
        self.posLabel = builder.get_object('posLabel')
        self.colorArea = builder.get_object('colorArea')
        self.colorLabel = builder.get_object('colorLabel')

        #when an image arrives, its data is stored here, a dict type when not None
        self.imageData = None
        
        #the pixbuf used to load image
        self.pixbuf = None
        
        #the real size of image being displayed originally
        self.imgRealSize = None
        
        #the size of the image, as it appears on the screen
        self.imgDisplaySize = None
        
        #the x and y scale, used for RESIZE mode
        self.scale = None
        
        #used for SCROLL mode when user zooms in/out
        self.globalScale = 1,1
        
        #the offset from the drawing layer at which image is drawn
        self.offset = None
        
        #the image being displayed, a simplecv Image object, set only when
        #necessary
        self.image = None
        
        #the unadulterated image
        self.noFilterImage = None
        
        self.window.set_title(self.title)
        self.window.show_all()
        self.builderWindow.show_all()

        #size of the window
        self._winWidth, self._winHeight = self.window.get_size()

        #updates whenever mouse motion occurs
        self._position = None

        #these values are updated by the mouse* functions
        self._mouseX = None
        self._mouseY = None
        self._leftMouseDownPos = None
        self._rightMouseDownPos = None
        self._leftMouseUpPos = None
        self._rightMouseUpPos = None
        self._middleMouseDownPos = None
        self._middleMouseUpPos = None
        self._scrollPos = None
        self._scrollDir = None

        #things to hide
        if(self.fit == Display.RESIZE):
            toolbar = builder.get_object('toolbar')
            toolbar.hide()
        
        if(self.type_ == Display.FULLSCREEN):
            self.window.fullscreen()
        elif(self.type_ == Display.FIXED):
            self.drawingArea.set_size_request(*self.size)
            self.window.set_resizable(False)
        elif(self.type_ == Display.DEFAULT):
            #self.drawingArea.set_size_request(*self.size)
            self.drawingArea.set_size_request(*self.size)
        else:
            raise ValueError("The Display type was not understood")
        if(self.fit == Display.RESIZE):
            self.scrolledWindow.set_policy(self.gtk.POLICY_NEVER, self.gtk.POLICY_NEVER)
        elif(self.fit == Display.SCROLL):
            self.scrolledWindow.set_policy(self.gtk.POLICY_AUTOMATIC, self.gtk.POLICY_AUTOMATIC)
        else:
            raise ValueError("The fit method was not understood")

        #calls pollMsg when gtk is idle.
        #Gtk calls this function when it has nothing else to do. This ensures 
        #that the worker repeatedly checks for arriving messages
        gobject.idle_add(self.pollMsg,None)

        gtk.main()

    def pollMsg(self,data=None):
        """
        
        **SUMMARY** 
        
        Checks the connection to see id there are any requests from the parent
        
        **PARAMETERS**
        
        * *data* - Required for the gtk callback, always None.
        
        """

  
        #check if there is any data to be read, wait for 10ms
        #Is used because select.select/poll and gobject.idle_add dont work on windows
        dataThere = self.connection.poll(.001)
        
        #handle data if it's there
        if(dataThere):
            self.checkMsg()
            
        #required so that event handler stays enabled
        return True
        
    def checkMsg(self):
        """
        
        **SUMMARY**
        
        Reads the message from the parent and figures out what to do
        
        """
        
        #examine the message and figure out what to do with it
        msg = self.connection.recv()

        # A request from parent for the function 'XX' will call 'handle_XX' over
        # here

        funcName = "handle_" + msg['function']
        funcToCall = self.__getattribute__(funcName)
        funcToCall(msg)

            
    def handle_showImage(self,data):
        """
        
        **SUMMARY**
        
        Display the image requested by the parent
        
        **PARAMETERS**
        
        * *data* - The dict sent by the parent contaning the image data.
        
        """
        #show image from string
    
        #invalidate existing image
        self.image = None
        self.noFilterImage = None
        self.imageData = data
        self.imgRealSize = (data['width'],data['height'])
        
        #convert the string to a pixbuf
        self.pixbuf =  self.gtk.gdk.pixbuf_new_from_data(data['data'], self.gtk.gdk.COLORSPACE_RGB, False, data['depth'], data['width'], data['height'], data['width']*3)
        
        # tell gtk to draw again
        self.drawingArea.queue_draw()
        
        if(self.type_ == Display.DEFAULT):
            #enlarge display to show the image
            self.viewPort.set_size_request(data['width']+25,data['height']+25)
        elif(self.type_ == Display.FIXED):
            pass
        
    def handle_close(self,widget,data=None):
    
        #http://img.tapatalk.com/d/12/09/13/4yzanezu.jpg
        self.connection.send('Kill Me')
        self.window.hide()
        
        #Calling gtk.main_quit() stalls the parent application. This is because
        #The child quits and parent blocks till the child can receive data
        #
        #Instead we send the parent a message so that it terminates the child.
        #This way the child can continue to receive a message that the parent 
        #might be sending and the parent knows exactly when the display is 
        #closed. 
        #
        #Closing merely hides the display. The parent terminate the process
        #when it reads 'Kill Me'
        
    def handle_getImageWidgetSize(self,data):
        """
        
        **SUMMARY**
        
        Send the area occupied by drawingArea to parent.
        
        """
        self.connection.send((self.drawingArea.get_allocation().width,self.drawingArea.get_allocation().height))

    def handle_configure_event(self,widget,event):
        """

        **SUMMARY**

        Updates the windows dimension in the variable as soon as the window is reconfigure(resized,etc)
        These variable are used in other funtions.

        """
        self._winWidth = event.width
        self._winHeight = event.height

    def handle_mouseX(self,data):
        """

        **SUMMARY**

        Sends the current X coordinate of the mouse position on the image. 

        *NOTE* 

        If the display is initialized with fit= RESIZE, the coordinates returned
        are according to the size of the image. For example, if the image is 512x512, then 
        the bottom left corner of the image will have mouse X position returned as 512, even if 
        the display is resized to make the image bigger or smaller. To get the position of 
        the mouse pointer as visible on the screen use the mousePositionRaw.
        

        """
        if self._position is not None:
            pos = self._clamp(self._mouseOffset(self._position))[0]
            pos = int(pos/self.scale[0])
        else:
            pos = None
        self.connection.send(pos)
        
    def handle_mouseY(self,data):
        """

        **SUMMARY**

        Sends the current Y coordinate of the mouse position on the image.

        *NOTE* 

        If the display is initialized with fit= RESIZE, even then the coordinates returned
        are according to the size of the image. For example, if the image is 512x512, then 
        the bottom left corner of the image will have mouse X position returned as 512, 
        even if the display is resized to make the image bigger or smaller.
        To get the position of the mouse pointer as visible on the screen use the mousePositionRaw().
        

        """        
        if self._position is not None:
            pos = self._clamp(self._mouseOffset(self._position))[1]
            pos = int(pos/self.scale[1])
        else:
            pos = None
        self.connection.send(pos)
        
    def mouse_motion(self,widget,event):
        """
        
        **SUMMARY**
        
        Updates the mouse position whenever mouse pointer moves
        
        """

        #initially when there is no image
        if(not self.offset):
            return
        self._position = (event.x,event.y)
        x = int((event.x - self.offset[0])/self.scale[0])
        y = int((event.y - self.offset[1])/self.scale[1])
        w,h = self.pixbuf.get_width(),self.pixbuf.get_height()
        x = min(max(x,0),w-1)
        y = min(max(y,0),h-1)
        self.posLabel.set_text(`(x,y)`)
        r,g,b = color = self.pixbuf.pixel_array[y,x]
        self.colorLabel.set_label(`(r,g,b)`)
        r,g,b = float(r)/255,float(g)/255,float(b)/255
        

        cr = self.colorArea.window.cairo_create()
        w = self.colorArea.get_allocation().width
        h = self.colorArea.get_allocation().height
        cr.set_source_rgb(r,g,b)
        cr.rectangle(0,0,w,h)
        cr.fill()
        
    def mouse_press(self,widget,event):
        """
        
        **SUMMARY**
        
        This function is called autmatically whenever a mouse button is pressed(goes down).
        It checks which of mouse button(Left, Right, or Middle) is pressed and assigns the 
        position where the mouse was pressed to the corresponding button's press(down) variable.
         
        """
        if event.button == 1 :
            self._leftMouseDownPos = (event.x,event.y)
        if event.button == 2 :
            self._middleMouseDownPos = (event.x,event.y)
        if event.button == 3:
            self._rightMouseDownPos = (event.x,event.y)

    def mouse_release(self,widget,event):
        """
        
        **SUMMARY**
        
        This function is called autmatically whenever a mouse button is released(goes up).
        It checks which of mouse button(Left, Right, or Middle) is released and assigns the 
        position where the mouse was released to the corresponding button's release(up) variable.
         
        """
        if event.button == 1 :
            self._leftMouseUpPos = (event.x,event.y)
        if event.button == 2 :
            self._middleMouseUpPos = (event.x,event.y)
        if event.button == 3:
            self._rightMouseUpPos = (event.x,event.y)

    def mouse_scroll(self,widget,event):
        """
        
        **SUMMARY**
        
        This function is called autmatically whenever a mouse is scrolled.
        It assigns the position where the mouse was scrolled and the direction of the scroll
        (up or down) to the corresponding variables.
         
        """
        self._scrollPos = (event.x,event.y)
        if str(event.direction) == '<enum GDK_SCROLL_UP of type GdkScrollDirection>':
            self._scrollDir = 'up'
        elif str(event.direction) == '<enum GDK_SCROLL_DOWN of type GdkScrollDirection>':
            self._scrollDir = 'down'

    def _clamp(self,pos):
        """
        
        **SUMMARY**
        
        Clamps the values of the mouse psotion to the size of the image

        **PARAMETERS**

        * *pos* - The position coordinates to be clamped in the form of (x,y) tuple

        """
        pos = list(pos)
        if pos[0] < 0:
            pos[0] = 0
        elif pos[0] > self.imgDisplaySize[0]:
            pos[0] = self.imgDisplaySize[0]
        if pos[1] < 0:
            pos[1] = 0
        elif pos[1] > self.imgDisplaySize[1]:
            pos[1] = self.imgDisplaySize[1]
        return tuple(pos)


    def _mouseOffset(self,pos):
        """
        
        **SUMMARY**
        
        Set the correct offset for the mouse position so that the top left corner  

        **PARAMETERS**

        * *pos* - The position coordinates to be clamped in the form of (x,y) tuple
        
        """
        diff = self.offset
        return (pos[0]-diff[0],pos[1]-diff[1])


    def handle_leftDown(self, data):
        """
        
        **SUMMARY**
        
        Sends the position where the left mouse button was pressed.
        
        """
        if self._leftMouseDownPos is not None:
            p = self._clamp(self._mouseOffset(self._leftMouseDownPos))
            p = (int(p[0]/self.scale[0]),int(p[1]/self.scale[1]))
        else:
            p = None
        self.connection.send((p,))
        self._leftMouseDownPos = None

    def handle_rightDown(self, data):
        """
        
        **SUMMARY**
        
        Sends the position where the right mouse button was pressed.
        
        """
        if self._rightMouseDownPos is not None:
            p = self._clamp(self._mouseOffset(self._rightMouseDownPos))
            p = (int(p[0]/self.scale[0]),int(p[1]/self.scale[1]))
        else:
            p = None
        self.connection.send((p,))
        self._rightMouseDownPos = None

    def handle_leftUp(self,data):
        """
        
        **SUMMARY**
        
        Sends the position where the left mouse button was released.
        
        """
        if self._leftMouseUpPos is not None:
            p = self._clamp(self._mouseOffset(self._leftMouseUpPos))
            p = (int(p[0]/self.scale[0]),int(p[1]/self.scale[1]))
        else:
            p = None
        self.connection.send((p,))
        self._leftMouseUpPos = None

    def handle_rightUp(self,data):
        """
        
        **SUMMARY**
        
        Sends the position where the right mouse button was released.
        
        """
        if self._rightMouseUpPos is not None:
            p = self._clamp(self._mouseOffset(self._rightMouseUpPos))
            p = (int(p[0]/self.scale[0]),int(p[1]/self.scale[1]))
        else:
            p = None
        self.connection.send((p,))
        self._rightMouseUpPos = None

    def handle_middleDown(self,data):
        """
        
        **SUMMARY**
        
        Sends the position where the middle mouse button was pressed
        
        """
        if self._middleMouseDownPos is not None:
            p = self._clamp(self._mouseOffset(self._middleMouseDownPos))
            p = (int(p[0]/self.scale[0]),int(p[1]/self.scale[1]))
        else:
            p = None
        self.connection.send((p,))
        self._middleMouseDownPos = None

    def handle_middleUp(self,data):
        """
        
        **SUMMARY**
        
        Sends the position where the middle mouse button was released.
        
        """
        if self._middleMouseUpPos is not None:
            p = self._clamp(self._mouseOffset(self._middleMouseUpPos))
            p = (int(p[0]/self.scale[0]),int(p[1]/self.scale[1]))
        else:
            p = None
        self.connection.send((p,))
        self._middleMouseUpPos = None

    def handle_mouseScrollPosition(self,data):
        """
        
        **SUMMARY**
        
        Sends the position where the mouse was scrolled.
        
        """
        if self._scrollPos is not None:
            p = self._clamp(self._mouseOffset(self._scrollPos))
            p = (int(p[0]/self.scale[0]),int(p[1]/self.scale[1]))
        else:
            p = None
        self.connection.send((p,))
        self._scrollPos = None

    def handle_mouseScrollType(self,data):
        """
        
        **SUMMARY**
        
        Sends the direction of the mouse scroll ('up' or 'down')
        
        """
        self.connection.send((self._scrollDir,))
        self._scrollDir = None

    def draw(self,widget,eventData = None):
        """
        
        **SUMMARY**
        
        Does the actual displaying of the received image data
        
        **PARAMETERS**
        
        * *widget* - The widget to draw on. In this case, drawingArea
        
        * *eventData* - None always
        
        """
        
        if(self.pixbuf == None):
            return
        if(self.type_ == Display.DEFAULT):
            #so that window can be resized to almost any size later
            self.scrolledWindow.set_size_request(10,10)  
    
        if(self.fit == Display.SCROLL):
            #no resizing required
            pix = self.pixbuf
            
        elif(self.fit == Display.RESIZE):
            #resize the image to fit drawingArea
            areaWidth = self.drawingArea.get_allocation().width
            areaHeight = self.drawingArea.get_allocation().height
            pix = smartScale(self.gtk.gdk,self.pixbuf,(areaWidth,areaHeight))
            
        cr = widget.window.cairo_create()

        #cr.scale(areaWidth,areaHeight)    
        if(self.fit == Display.SCROLL):
            #No scaling, no offset, the image is displayed as is. Scrollbars
            #take care of the excess part
            self.imgDisplaySize = self.imgRealSize
            self.offset = 0,0
            self.scale = self.globalScale
            self.imgDisplaySize = int(self.imgDisplaySize[0]*self.globalScale[0]),int(self.imgDisplaySize[1]*self.globalScale[1])
            sr = int(self.imgDisplaySize[0]),int(self.imgDisplaySize[1])
            self.drawingArea.set_size_request(*sr)
        elif(self.fit == Display.RESIZE):
            # reduce the request so the window can be shrunk to lesser than the
            # image size
            self.drawingArea.set_size_request(10,10)
            
            self.imgDisplaySize =  (int(pix.get_width()),int(pix.get_height()))
            self.offset = self.getCentreOffset()
            self.scale = float(self.imgDisplaySize[0])/self.imgRealSize[0] , float(self.imgDisplaySize[1])/self.imgRealSize[1]
            
            #paint the background
            cr.set_source_rgb(*GtkWorker.BGCOLOR) # blue
            cr.rectangle(0, 0, areaWidth, areaHeight)
            cr.fill()
        
        # clip, so that drawings dont go outside the image
        x,y,w,h = self.offset[0],self.offset[1],self.imgDisplaySize[0],self.imgDisplaySize[1]
        cr.rectangle(x,y,w,h)
        cr.clip()
        
        #draw the image
        if(self.fit == Display.SCROLL):
            cr.scale(*self.globalScale)
            cr.set_source_pixbuf(pix,self.offset[0],self.offset[1])
            cr.paint()
        else:
            cr.set_source_pixbuf(pix,self.offset[0],self.offset[1])
            cr.paint()
            cr.translate(*self.offset)
            cr.scale(*self.scale)

        
        #scale and translate the drawings

        
        self.drawLayers(cr)
        
    def drawLayers(self,context):
        """
        
        **SUMMARY**
        
        Draws the layers of the image
        
        **PARAMETERS**
        
        * *context* - The Cairo Context to be used for drawing.
        
        """
        if(self.imageData is None):
            return
        layers = self.imageData['layers']
        for layer in layers:
            
            for shape in layer.shapes():
                drawShape(context,shape)
                
        
    def getCentreOffset(self):
        """
        
        **SUMMARY**
        
        Returns the offset ( the amount by which top-left corener is displaced)
        of the image.
        
        **RETURNS**
        
        A (x,y) tuple.
        
        """
        area = self.drawingArea.get_allocation().width, self.drawingArea.get_allocation().height
        imgSize = self.imgDisplaySize
        return (area[0] - imgSize[0])/2, (area[1] - imgSize[1])/2 
    
    def getImage(self):
        """
        
        **SUMMARY** 
        
        Converts received data into a SimpleCV image.
        
        **RETURNS**
        
        A SimpleCV image.
        
        """
        
        if(self.image == None):
            array = np.fromstring(self.imageData['data'],dtype='uint8')
            array = array.reshape(self.imageData['width'],self.imageData['height'],3)
            array = np.swapaxes(array,0,1)
            self.image = Image(array)
        return self.image
            
    def handle_mousePosition(self, data):
        """
        
        **SUMMARY**
        
        Sends the position of the mouse on the image. Returns None if mouse pointer
        is not on the image. use this for any kind of image manipulation
 
        *NOTE* 

        If the display is initialized with fit= RESIZE, the coordinates returned
        are according to the size of the image. For example, if the image is 512x512, then 
        the bottom left corner of the image will have mouse position returned as (512,512) even if 
        the display is resized to make the image bigger or smaller. To get the position of 
        the mouse pointer as visible on the screen use the mousePositionRaw.
 
        """
        if self._position is not None:
            pos = self._clamp(self._mouseOffset(self._position))
            pos = (int(pos[0]/self.scale[0]),int(pos[1]/self.scale[1]))
        else:
            pos = None
        self.connection.send(pos)

    def handle_mousePositionRaw(self,data):
        """
        
        **SUMMARY**
        
        Sends the position of the mouse pointer on the whole display
        
        """
        self.connection.send(self._position)
    
    def zoomIn(self,data=None):
        """
        
        **SUMMARY**
        
        Zoom into the image, handler for the Zoom in callback
        
        """
        self.globalScale = self.globalScale[0] + 0.1,self.globalScale[1] + 0.1
        self.drawingArea.queue_draw()
    def zoomOut(self,data=None):
        """
        
        **SUMMARY**
        
        Zoom out of the image, handler for the Zoom Out callback
        
        """
        self.globalScale = self.globalScale[0] - 0.1,self.globalScale[1] - 0.1
        self.drawingArea.queue_draw()
    def fullscreen(self,data = None):
    
        """
        
        **SUMMARY**
        
        Toggle fullscreen
        
        
        """
        if(data.get_active()):
            self.window.fullscreen()
        else:
            self.window.unfullscreen()
        
    def saveDisplay(self,data = None):
        """
        
        **SUMMARY**
        
        Launches a dialog box to save the image. The image is saved as it is visible
        with all its drawings and filters applied. The image is not scaled
        """
        
        #TODO this is totally broken, needs to be done with mergeLayers
        
        dest = self.gtk.gdk.Pixbuf(self.gtk.gdk.COLORSPACE_RGB,False,8,self.imgDisplaySize[0],self.imgDisplaySize[1])
        colormap = self.drawingArea.window.get_colormap()
        pixbuf = self.gtk.gdk.Pixbuf(self.gtk.gdk.COLORSPACE_RGB, 0, 8, *self.imgDisplaySize)
        pixbuf.get_from_drawable(self.drawingArea.window,colormap,self.offset[0],self.offset[1],0,0,*self.imgDisplaySize) 
        
        
        
        
        chooser = self.gtk.FileChooserDialog(title="Save Image",action=self.gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(self.gtk.STOCK_CANCEL,self.gtk.RESPONSE_CANCEL,self.gtk.STOCK_SAVE,self.gtk.RESPONSE_OK))
        chooser.set_default_response(self.gtk.RESPONSE_CANCEL)
        filter = self.gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        chooser.add_filter(filter)
        
        response = chooser.run()
        if response == self.gtk.RESPONSE_OK:
            name = chooser.get_filename()
            if(name.upper().endswith(".JPG")):
                pixbuf.save(name,"jpeg", {"quality":"100"})
            elif(name.upper().endswith(".PNG")):
                pixbuf.save(name,"png",{})
            else:
                md = self.gtk.MessageDialog(None,flags = 0 ,
                    type =  self.gtk.MESSAGE_ERROR, 
                    buttons = self.gtk.BUTTONS_CLOSE)
                md.set_markup("Unsupported Extension\nOnly JPG and PNG are supported")
                md.run()
                md.destroy()
        chooser.destroy()
        
    def findLines(self,data=None):
        img = self.getImage()
        fs = img.findLines()
        fs.draw(width = 2)
        self.putImage(img)
        pass

    def findCircles(self, data = None):
        img = self.getImage()
        fs = img.findCircle()
        fs.draw(width = 2)
        self.putImage(img)
        pass

    def findCorners(self,data=None):
        img = self.getImage()
        fs = img.findCorners()
        fs.draw(width = 2)
        self.putImage(img)
        pass

    def putImage(self,img):
    
        """
        
        **SUMMARY**
        
        Displays the image specified on the diplsay
        
        **PARAMETERS**
        * *img* - The image to be displayed

        """
        dic = {}
        dic['function'] = 'showImage'
        dic['data'] = img.toString()
        dic['depth'] = img.depth
        dic['width'] = img.width
        dic['height'] = img.height
        dic['layers'] = img.layers()
        
        self.image = None
        self.imageData = dic
        self.imgRealSize = (img.width,img.height)
        
        #convert the string to a pixbuf
        self.pixbuf =  self.gtk.gdk.pixbuf_new_from_data(dic['data'], self.gtk.gdk.COLORSPACE_RGB, False, dic['depth'], dic['width'], dic['height'], dic['width']*3)
        
        # tell gtk to draw again
        self.drawingArea.queue_draw()
        
    def addFilter(self,data=None):
        """
        
        **SUMMARY**
        
        The call baxk handler for add filter button
        """

        model,iterator =  self.filterTreeview.get_selection().get_selected()
        if(iterator):
            path = model.get_path(iterator)
            index = path[0]
            filter_ =  model[index][0]
            self.applyListStore.append((filter_,))
            
        self.applyListStore.foreach(self.applyFilter,None)
            
    def removeFilter(self,data=None):
        """
        
        **SUMMARY**
        
        The call baxk handler for remove filter button
        """
        model,iterator =  self.applyTreeview.get_selection().get_selected()
        if(iterator):
            model.remove(iterator)
            
        
        self.putImage(self.noFilterImage)
        self.applyListStore.foreach(self.applyFilter,None)
    
    def applyFilter(self,model, path, iterator,data=None):
        """
        
        **SUMMARY**
        
        Applies the filter corresponding to iterator to the image
        """
        if( not self.noFilterImage ):
            self.noFilterImage = self.getImage()
        path = model.get_path(iterator)
        index = path[0]
        filter_ = model[index][0]
        img = self.getImage()
        function = getattr(img,filter_)
        newImg = function()
        self.putImage(newImg)

