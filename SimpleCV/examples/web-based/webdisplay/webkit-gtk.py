import gtk
import webkit

view = webkit.WebView()

sw = gtk.ScrolledWindow()
sw.add(view)

win = gtk.Window(gtk.WINDOW_TOPLEVEL)
win.resize(800,600)
win.add(sw)
win.show_all()

view.open("http://localhost:5000/")
gtk.main()
