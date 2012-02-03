#!/usr/bin/python
'''
This program just shows off a simple example of using GTK with SimpleCV

It's a very simple way to update an image using python and GTK.
The image is being updated as the slider is moved.
The only amount of SimpleCV code is found in the process_image() function

'''

print __doc__

import gtk
import SimpleCV


class app(gtk.Window):

	#Program Settings (You can change these)
	edge_threshold = 100
	max_threshold = 500
	min_threshold = 0
	window_width = 500
	window_height = 500
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

		
		self.current_image = image
		self.add(vbox)
		self.show_all()


	'''
	This is where you can do any of your SimpleCV processing
	it returns a Numpy array as that is what is handled by GTK
	'''
	def process_image(self):
		#Start SimpleCV Code
		img = SimpleCV.Image('lenna').rotate90()
		edges = img.edges(self.edge_threshold)
		numpy_img = edges.getNumpy()
		#End SimpleCV Code
		return numpy_img
		

	#This function is called anything the slider is moved
	def update_threshold(self, w):
		#grab the value from the slider
		self.edge_threshold = w.get_value()

		updated_image = self.process_image()
		converted_image = gtk.gdk.pixbuf_new_from_array(updated_image, gtk.gdk.COLORSPACE_RGB, 8)
		self.current_image.set_from_pixbuf(converted_image)
		self.show_all()

'''
Just create multiple instances of the object to have multiple windows
with varying control on each window.  These could also be extended using
threading so they could talk together, or if you closed one, it wouldn't
close the others, etc.
'''
program1 = app()
program2 = app()
gtk.main()
