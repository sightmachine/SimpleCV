'''
This application uses Flask as a web server and jquery to trigger
pictures with SimpleCV

To use start the web server:
>>> python flask-server.py

Then to run the application:
>>> python webkit-gtk.py

*Note: You are not required to run the webkit-gtk.py, you can also
visit http://localhost:5000

'''

print __doc__


from flask import Flask, jsonify, render_template, request
from werkzeug import SharedDataMiddleware
import tempfile, os
import simplejson as json
import SimpleCV


app = Flask(__name__)
cam = SimpleCV.Camera()

@app.route('/')
def show(name=None):
    img = cam.getImage()
    tf = tempfile.NamedTemporaryFile(suffix=".png")
    loc = 'static/' + tf.name.split('/')[-1]
    tf.close()
    img.save(loc)
    return render_template('index.html', img=loc)

@app.route('/_snapshot')
def snapshot():
    '''
    Takes a picture and returns a path via json
    used as ajax callback for taking a picture
    '''
    img = cam.getImage()
    tf = tempfile.NamedTemporaryFile(suffix=".png")
    loc = 'static/' + tf.name.split('/')[-1]
    tf.close()
    img.save(loc)
    print "location",loc
    print "json", json.dumps(loc)
    return json.dumps(loc)

if __name__ == '__main__':
    if app.config['DEBUG']:
        from werkzeug import SharedDataMiddleware
        import os
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
                '/': os.path.join(os.path.dirname(__file__), 'static')
        })
    app.run()
