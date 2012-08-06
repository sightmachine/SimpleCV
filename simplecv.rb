require 'formula'

class Simplecv < Formula
  head 'git://github.com/ingenuitas/SimpleCV.git'
  homepage 'http://www.simplecv.org/'
  #url 'https://github.com/downloads/ingenuitas/SimpleCV/simplecv.tar.gz'
  md5 'ab524249721152955f68bf54c2744400'

  depends_on 'libtiff' => :build
  depends_on 'sdl' => :build
  depends_on 'sdl_image' => :build
  depends_on 'sdl_mixer' => :build 
  depends_on 'sdl_ttf' => :build
  #depends_on 'smpeg' => :build 
  depends_on 'portmidi' => :build
  depends_on 'hg' => :build 
  depends_on 'opencv' => :build
  depends_on 'python' => :build


  def install
    # uhg
    # http://stackoverflow.com/questions/4393830/how-do-i-set-up-a-local-python-library-directory-pythonpath
    #  sudo ARCHFLAGS="-arch i386 -arch x86_64" pip install  --ignore-installed --install-option="--prefix=/usr/local" --verbose hg+http://bitbucket.org/pygame/pygame

    #
    #ARCHFLAGS="-arch i386 -arch x86_64"
    #sudo pip install hg+http://bitbucket.org/pygame/pygame
    #looks like we need to append python setup.py install --home=HOMEBREW_PREFIX/lib/python2.7/site-packages
    system "sudo ARCHFLAGS=\"-arch i386 -arch x86_64\" pip install  --ignore-installed --install-option=\"--prefix=#{HOMEBREW_PREFIX}\" --verbose -r requirements.txt"
    system "sudo python setup.py install --prefix=#{HOMEBREW_PREFIX}"

  end

  def test
    #system "false"
  end
end
