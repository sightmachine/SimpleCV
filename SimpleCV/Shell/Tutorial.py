#!/usr/bin/python

# A Basic SimpleCV interactive shell tutorial

#load required libraries
from SimpleCV import *

from subprocess import call
from code import InteractiveInterpreter
import platform

lb = "\n" #linebreak
tb = "\t" #tab
tutorial_interpreter = InteractiveInterpreter(globals())
logo = None
img = None
clone = None
thumb = None
eroded = None
cropped = None

#Command to clear the shell screen
def shellclear():
    if platform.system() == "Windows":
      return
    call("clear")

def attempt(variable_name, desired_class):
    prompt_and_run()
    variable = globals().get(variable_name)

    if isinstance(variable,desired_class):
        if desired_class == Image:
            if variable.isEmpty():
                print lb
                print "Although you can create empty Images on SimpleCV, let's not"
                print "play with that now!"
                print lb
                return False

        return True

    return False 

def prompt_and_run():

    command = raw_input("SimpleCV:> ")
    tutorial_interpreter.runsource(command)
    return command

def request_show_command():
    while True:
        if prompt_and_run().endswith('.show()'):
            return

def end_tutorial():
    print lb
    print "Type 'quit' to leave the tutorials, or press Enter to move on!"
    command = raw_input("SimpleCV:> ")
    return command.lower() == 'quit'

def end_of_tutorial():
    print lb
    print "This is the end of our tutorial!"
    print lb
    print "For more help, go to www.simplecv.org, and don't forget about the"
    print "help function!"
    print lb

def command_loop(command, desired_tuple):
    while True:
        print command
        print lb

        if attempt(desired_tuple[0], desired_tuple[1]):
            return

        print lb
        print "Oops! %s is still not %s" % (desired_tuple[0], str(desired_tuple[1]))

def tutorial_image():
    shellclear()
    print "SimpleCV Image tutorial"
    print "-----------------------"
    print lb
    print "Using images are simple, in SimpleCV."
    print lb
    print "First thing we are going to do is load an image. Try it yourself:"
    print lb

    cmd = "logo = Image(\"simplecv\")"
    desired_tuple = ('logo', Image)
    command_loop(cmd, desired_tuple)

    print lb
    print "Correct! You just loaded SimpleCV logo into memory."
    print "Let's try it to use one of your images. There are different ways to"
    print "do that. You can try, for example:"
    print lb
    print "img = Image(URL_TO_MY_PICTURE) or img = Image(PATH_TO_MY_PICTURE)"
    print lb
    cmd =  "Example: img = Image('http://simplecv.org/images/logo.gif')"

    desired_tuple = ('img', Image)
    command_loop(cmd, desired_tuple)

    print lb
    print "Perfect! Now we want to see it:"
    print lb
    cmd = "img.show()"
    print cmd
    print lb

    request_show_command()

    print lb
    print "Alright! This was tutorial 1/6."
    print "Next tutorial: Saving Images"
    if not end_tutorial():
        tutorial_save()
    return

def tutorial_save():
    shellclear()
    print "Saving Images"
    print lb
    print "Once you have an Image Object loaded in memory you can"
    print "now save it to disk."
    print lb
    raw_input("[Press enter to continue]")
    print lb
    print "Saving an image is very simple, pardon the pun. Once it's loaded"
    print "into memory, it's literally just:"
    print "img.save()"
    print lb
    print "This will save the image back to the location it was loaded from"
    print "so if you did img = Image('/tmp/test.jpg'), then it would save"
    print "it back there, otherwise you can do:"
    print "img.save('/any/path/you/want')"
    print lb
    print "So try it now and save an image somewhere on your system"
    print lb

    if platform.system() == "Windows":
        print "img.save('C:/myimg.jpg')"
    else:
        print "img.save('/tmp/new.jpg')"

    print lb

    while True:
        if prompt_and_run().startswith('img.save'):
            break
        print "Please try to save img!"
        print lb

    print "Correct, you just saved a new copy of your image!"
    print "As you can see in SimpleCV most of the functions are intuitive."

    print lb
    print "Alright! This was tutorial 2/6."
    print "Next tutorial: Camera"
    if not end_tutorial():
        tutorial_camera()
    return


def tutorial_camera():
    shellclear()
    print "Camera"
    print lb
    print "As long as your camera driver is supported then you shouldn't have a"
    print "problem. Type 'skip' to skip the camera tutorial, or press Enter to"
    print "continue."
    print lb

    command = raw_input("SimpleCV:> ")
    if command.lower() != 'skip':
        print lb
        print "To load the camera, just type:"
        print lb

        cmd = "cam = Camera()"
        desired_tuple = ('cam', Camera)
        command_loop(cmd, desired_tuple)

        print lb
        print "Next, to grab an image from the Camera we type:"
        cmd = "img = cam.getImage()"
        tutorial_interpreter.runsource("del(img)")
        desired_tuple = ('img', Image)
        command_loop(cmd, desired_tuple)

        print "Just as before, if we want to display it, we just type:"
        print lb
        print "img.show()"
        print lb

        request_show_command()

    print lb
    print "Alright! This was tutorial 3/6."
    print "Next tutorial: Copying Images"
    if not end_tutorial():
        tutorial_copy()
    return

def tutorial_copy():
    shellclear()
    print "Copying Images"
    print lb
    print "If you need a copy of an image, this is also very simple:"
    print "Let's try to clone img, which we already have."

    global img
    if not img:
        img = Image("lenna")

    print lb
    cmd = "clone = img.copy()"
    desired_tuple = ('clone', Image)

    while True:
        command_loop(cmd, desired_tuple)
        if clone != img: #Returns False if they have different addresses.
            break

        print "You have to use the copy() function!"

    print lb
    print "Correct, you just cloned an image into memory."
    print "You need to be careful when using this method though as using as a"
    print "reference vs. a copy.  For instance, if you just typed:"
    print lb
    print "clone = img"
    print lb
    print "clone would actually point at the same thing in memory as img."

    print lb
    print "Alright! This was tutorial 4/6."
    print "Next tutorial: Manipulating Images"
    if not end_tutorial():
        tutorial_manipulation()
    return

def tutorial_manipulation():
    shellclear()
    print "Manipulating Images"
    print lb
    print "Now we can easily load and save images. It's time to start doing some"
    print "image processing with them. Let's make img, which we already have, a"
    print "90x90 thumbnail:"

    global img
    if not img:
        img = Image("lenna")

    print lb
    cmd = "thumb = img.scale(90,90)"
    desired_tuple = ('thumb', Image)

    while True:
        command_loop(cmd, desired_tuple)
        if thumb.size() == (90,90):
            break

        print "Your thumbnail's size isn't 90x90! Try again!"

    print lb
    print "Now display it with thumb.show()"
    print lb
    request_show_command()

    print lb
    print "Now let's erode the picture some:"
    print lb
    cmd = "eroded = img.erode()"
    desired_tuple = ('eroded', Image)
    command_loop(cmd, desired_tuple)

    print lb
    print "Display it with eroded.show(). It should look almost as if the image"
    print "was made if ink and had water spoiled on it."
    print lb
    request_show_command()

    print lb
    print "Last but not least, let's crop a section of the image out:"
    print lb
    cmd = "cropped = img.crop(100, 100, 50, 50)"
    desired_tuple = ('cropped', Image)
    command_loop(cmd, desired_tuple)

    print lb
    print "Use cropped.show() to display it."
    print lb
    request_show_command()
    print lb
    print "That went from the coordinate in (X,Y), which is (0,0) and is the"
    print "top left corner of the picture, to coordinates (100,100) in the"
    print "(X,Y) and cropped a picture from that which is 50 pixels by 50 pixels."

    print lb
    print "Alright! This was tutorial 5/6."
    print "Next tutorial: Features"
    if not end_tutorial():
        tutorial_features()
    return



def tutorial_slicing():
    shellclear()
    print "Slicing Images"
    print lb
    print "Slicing is sort of a new paradigm to access parts of an image."
    print "Typically in vision a region of interest (ROI) is given.  "
    print "In this case, slicing is a very powerful way to access parts"
    print "of an image, or basically any matrix in SimpleCV in general."
    print lb
    print "This is done by using:"
    print "section = img[1:10,1:10]"
    print lb
    print "What is returned is an image object with that window."
    print "the slicing basically acts like a ROI but returns an image"
    print "so if you wanted to say run edge detection on a 20x20 box"
    print "in the picture that started at x=5,y=10 you use:"
    print "foundedges = img[5:25,10:30].edges()"
    print lb
    raw_input("[Press enter to continue]")
    shellclear()
    in_text = ""
    shouldbe = "ROI = img[1:6,1:6]"
    print "Please type this now:"
    print shouldbe
    print lb
    while (in_text != shouldbe):
      in_text = raw_input("SimpleCV:>")
      if(in_text != shouldbe):
        print "sorry, that is incorrect"
        print "please type:"
        print shouldbe
    shellclear()
    print "Correct, you just returned a 5 pixel by 5 pixel image object"
    print lb
    return

def tutorial_features():
    shellclear()
    print "Features"
    print lb
    print "Features are things you are looking for in the picture. They can be"
    print "blobs, corners, lines, etc. Features are sometimes referred to as a"
    print "fidicual in computer vision. These features are something that is"
    print "measureable, and something that makes images unique. Features are"
    print "something like when comparing things like fruit. In this case the"
    print "features could be the shape and the color, amongst others."
    print lb
    print "What features are in SimpleCV is an abstract representation of that."
    print "You take your image, then perform a function on it, and get back"
    print "features or another image with them applied. The crop example is"
    print "a case where an image is returned after we perform something."
    print lb
    print "In a simple example we will use the famous 'lenna' image, and find"
    print "corners in the picture."
    print lb
    tutorial_interpreter.runsource("img = Image('lenna')")
    print "img = Image('lenna') (already done for you)"
    print lb
    print "Try it yourself:"
    print lb 
   
    cmd = "corners = img.findCorners()"
    desired_tuple = ('corners', FeatureSet)
    command_loop(cmd, desired_tuple)

    print lb
    print "Correct, you just got a featureset object which contains"
    print "feature objects.  These feature objects contain data from the"
    print "found corners"
    print lb
    
    print "Tip: If your are unsure what parameters to pass, you can always use"
    print "the built in help support by typing help(Image.findCorners). Keep in"
    print "mind that this help works for all of the functions available in"
    print "SimpleCV"
    print lb

    print "We can also do that with blobs. Try it:"
    print lb

    cmd = "blobs = img.findBlobs()"
    desired_tuple = ('blobs', FeatureSet)
    command_loop(cmd, desired_tuple)

    print lb
    print "Great, but..."
    print "When we show the image we won't notice anything different. This"
    print "is because we have to actually tell the blobs to draw themselves"
    print "on the image:"
    print lb
    print "blobs.draw()"
    print lb
    
    while True:
        if prompt_and_run().endswith('.draw()'):
            break
        print "No blobs have been drawn!"
        print lb

    print "Now use img.show() to see the changes!"
    print lb
    request_show_command()
    print lb
    raw_input("[Press enter to continue]")

    print lb
    print lb
    print "There's also a small trick built into SimpleCV to do this even faster"
    print lb
    tutorial_interpreter.runsource("img = Image('lenna')")
    print "img = Image('lenna') (already done for you)"
    print lb

    while True:
        print "img.findBlobs().show()"
        print lb
        if prompt_and_run().endswith('.show()'):
            break
        print "Nothing has been shown!"
        print lb

    print lb
    print "Alright! This was tutorial 6/6."
    #print "Next tutorial: ..."
    return

def magic_tutorial(self,arg):
    tutorials_dict = {'image': tutorial_image, 'save': tutorial_save,
                     'camera': tutorial_camera, 'manipulation': tutorial_manipulation,
                     'copy': tutorial_copy, 'features': tutorial_features} 


    if (arg == ""):
        shellclear()
        print "+--------------------------------+"
        print " Welcome to the SimpleCV tutorial "
        print "+--------------------------------+"
        print lb
        print "At anytime on the SimpleCV Interactive Shell you can type tutorial,"
        print "then press the tab key and it will autocomplete any tutorial that"
        print "is currently available."
        print lb
        print "Let's start off with Loading and Saving images!"
        print lb
        print lb
        raw_input("[Press enter to continue]")
        tutorial_image()
        end_of_tutorial()
        return
    else:
        if arg in tutorials_dict:
            tutorials_dict[arg]()
        else:
            print "%s is not a tutorial!" % arg
