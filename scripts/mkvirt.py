import os
import virtualenv, textwrap

here = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(here)

print "Creating SimpleCV Bootstrap Install Script: simplecv-bootstrap.py"

output = virtualenv.create_bootstrap_script(textwrap.dedent("""
import os, subprocess

def after_install(options, home_dir):
    base_dir = os.path.dirname(home_dir)
    logger.notify('Installing SimpleCV into Virtual Environment')

    os.chdir(home_dir)
    print 'Current Directory:', os.getcwd()
    print 'dir list:', os.listdir(os.getcwd())
    print 'Symlinking OpenCV'
    os.symlink('/usr/local/lib/python2.7/dist-packages/cv2.so', os.path.join(os.getcwd(),'lib/python2.7/site-packages/cv2.so'))
    os.symlink('/usr/local/lib/python2.7/dist-packages/cv.py', os.path.join(os.getcwd(),'lib/python2.7/site-packages/cv.py'))
    subprocess.call(['pwd'])
    os.mkdir('src')
    os.chdir('src')
    subprocess.call(['wget','-O','pygame.tar.gz','http://github.com/xamox/pygame/tarball/master'])
    subprocess.call(['tar','zxvf','pygame.tar.gz'])
    print 'Runing setup for pygame'
    subprocess.call(['ls'])
    os.chdir('../')
    print 'Current Directory:', os.getcwd()
    print os.getcwd()
    subprocess.call(['./bin/python','src/xamox-pygame-3e48d10/setup.py','install'])


"""))
f = open('simplecv-bootstrap.py', 'w').write(output)


#~ sudo apt-get install python-opencv python-setuptools python-pip gfortran g++ liblapack-dev libsdl1.2-dev libsmpeg-dev mercurial

#~ source bin/activate
#~ cd src/pygame
#~ python setup.py -setuptools install
#~ pip install https://github.com/sightmachine/SimpleCV/zipball/masteriii
#    call_subprocess(['python','setup.py','-setuptools','install'], show_stdout=True)
#call_subprocess([join(home_dir, 'bin', 'pip'),'install','-r','requirements.txt'], show_stdout=True)
