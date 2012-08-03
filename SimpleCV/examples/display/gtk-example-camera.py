#!/usr/bin/python
'''
This program just shows off a simple example of using GTK with SimpleCV

This example interfaces with a Camera in real time

It's a very simple way to update an image using python and GTK.
The image is being updated as the slider is moved.
The only amount of SimpleCV code is found in the process_image() function

'''

print __doc__

import gtk
import SimpleCV
import gobject

cam = SimpleCV.Camera()

class app(gtk.Window):

	#Program Settings (You can change these)
	edge_threshold = 100
	max_threshold = 500
	min_threshold = 0
	window_width = 500
	window_height = 500
	refresh_rate = 100 #in milliseconds
	#End Program Settings
	
	#Variables
	current_image = None

	#This function setup's the program
	def __init__(self):
		super(app, self).__init__()
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_title("Edge Threshold Adjuster")
		self.set_decorated(True)
		self.set_has_frame(False)
		self.set_resizable(False)
		self.set_default_size(self.window_width,self.window_height)
		self.connect("destroy", gtk.main_quit)
		vbox = gtk.VBox(spacing=4)


		#Setup the slider bar
		scale = gtk.HScale()
		scale.set_range(self.min_threshold, self.max_threshold)
		scale.set_size_request(500, 25)
		scale.set_value((self.max_threshold + self.min_threshold) / 2)
		scale.connect("value-changed", self.update_threshold)
		vbox.add(scale)

		#Setup the information label
		info = gtk.Label()
		info.set_label("Move the slider to adjust the edge detection threshold")
		vbox.add(info)

		#Add the image to the display
		new_image = self.process_image()
		converted_image = gtk.gdk.pixbuf_new_from_array(new_image, gtk.gdk.COLORSPACE_RGB, 8)
		image = gtk.Image()
		image.set_from_pixbuf(converted_image)
		image.show()
		vbox.add(image)


		gobject.timeout_add(self.refresh_rate, self.refresh)
		self.current_image = image
		self.add(vbox)
		self.show_all()


	def refresh(self):
		self.update_image()
		return True

	'''
	This is where you can do any of your SimpleCV processing
	it returns a Numpy array as that is what is handled by GTK
	'''
	def process_image(self):
		#Start SimpleCV Code
		img = cam.getImage().rotate90()
		edges = img.edges(self.edge_threshold)
		numpy_img = edges.getNumpy()
		#End SimpleCV Code
		return numpy_img

	def update_image(self):
		updated_image = self.process_image()
		converted_image = gtk.gdk.pixbuf_new_from_array(updated_image, gtk.gdk.COLORSPACE_RGB, 8)
		self.current_image.set_from_pixbuf(converted_image)
		self.show_all()
		

	#This function is called anything the slider is moved
	def update_threshold(self, w):
		#grab the value from the slider
		self.edge_threshold = w.get_value()
		self.update_image()


program1 = app()
gtk.main()
