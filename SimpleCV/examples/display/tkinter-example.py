import SimpleCV
import ImageTk #This has to be installed from the system repos
import tkinter
import time

tkinter.Tk()

image = SimpleCV.Image('http://i.imgur.com/FTKqh.jpg') #load the simplecv logo from the web
photo = ImageTk.PhotoImage(image.getPIL())
label = tkinter.Label(image=photo)
label.image = photo # keep a reference!
label.pack() #show the image
time.sleep(5)
