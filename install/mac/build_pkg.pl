#!/usr/bin/perl -w

use strict;
use Cwd qw(getcwd abs_path);
use File::Find qw(find);
use File::Path;
use File::Copy;

#script to take a functional build of simplecv and turn it
#into a file structure appropriate for the mac packagemaker
my $python_version = 2.6;
my $python_install_dir = "/Library/Python/$python_version/site-packages/";

#first, let's ID all the stuff we homebrew'd
my @homebrew_libs = qw(boost jpeg jasper libfreenect libtiff libusb-freenect little-cms opencv pil tbb);

#where the most recent/appropriate version of easy install is
my $easyinstall_location = "http://pypi.python.org/packages/$python_version/s/setuptools/setuptools-0.6c11-py$python_version.egg";

#what packages we need to postinstall
my @pkgs = qw(
  http://r.research.att.com/gfortran-42-5664.pkg
  http://github.com/downloads/oostendo/cvblob-python/cvblob-0.3.pkg
);

#the python libs we're going to bundle and easyinstall
my @python_libs = qw(
  http://sourceforge.net/projects/numpy/files/NumPy/1.6.1rc1/numpy-1.6.1rc1.tar.gz
  http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.0.1/matplotlib-1.0.1_r0-py2.6-macosx-10.3-fat.egg
  http://sourceforge.net/projects/scipy/files/scipy/0.9.0/scipy-0.9.0.tar.gz
  http://ipython.scipy.org/dist/0.10.2/ipython-0.10.2-py2.6.egg
);

my @python_lib_manual = qw(
  http://github.com/downloads/oostendo/cvblob-python/cvblob-python-macosx10.6-python2.6.tar.gz
);
    
my $python_install_directory = "/Library/Python/$python_version/site-packages/";

#look in the current directory, die if it's empty
#a little sad, but i didn't know until just now that
#you could use the diamond operator <> with a path
die "please start in an empty directory!" if (<./*>);

my $buildpath = getcwd();

foreach my $lib (@homebrew_libs) {
  my $libpath = "/usr/local/Cellar/" . $lib;
  die unless -e $libpath; 

  my @versions = <$libpath/*>;
  my $version_path = pop @versions;
  #get the most recent version of the app
  $version_path .= "/";

  find( sub {
    next if -d;
    my $fullpath = $File::Find::name;
    my ($relpath) = $fullpath =~ /$version_path(.*)$/; 
    #get the full path on the fs and the relative path

    my ($reldir) = $relpath =~ /^(.+)\/[^\/]+$/;    
    return if not $reldir; #we don't care about anything on the root 

    my $newdir = $buildpath . "/usr/local/".$reldir;
    mkpath($newdir) unless -d $newdir;
    #create the directory if we need to

    my $newpath = $buildpath . "/usr/local/".$relpath;
    copy($fullpath, $newpath);
    print "copying $fullpath -> $newpath \n";
    }, $version_path);
}

#now to get the remaining external packages 
my $extpkgpath = "/var/tmp/simplecv";
my $buildpkgpath = $buildpath . $extpkgpath;
mkpath($buildpkgpath);

my $postinstall_script = "#!/bin/sh\ncd $extpkgpath\n";

sub fetchPackage {
  chdir($buildpkgpath);
  my ($pkg_url) = @_;
  my ($fname) = $pkg_url =~ /^.+\/([^\/]+)$/;    
  `curl -O $fname $pkg_url`;
  chdir($buildpath);
  return $fname;
}

my $easyinstall_fname = fetchPackage($easyinstall_location);
$postinstall_script .= "\n#install easy_install\n";
$postinstall_script .= "./$easyinstall_fname\n";

$postinstall_script .= "\n#install external pkgs\n";
foreach my $pkg (@pkgs) {
  my $pkg_fname = fetchPackage($pkg);
  $postinstall_script .= "installer -pkg '$pkg_fname' -target '/'\n";
}

$postinstall_script .= "\n#install python deps\n";
foreach my $pylib (@python_libs) {
  my $pkg_fname = fetchPackage($pylib);
  $postinstall_script .= "easy_install $pkg_fname\n";
}

$postinstall_script .= "\n#install manual python deps\n";
foreach my $manuallib (@python_lib_manual) {
  my $pkg_fname = fetchPackage($manuallib);
  $postinstall_script .= "tar xzf $pkg_fname -C $python_install_dir\n";
}

$postinstall_script .= "\n#and finally, symlink opencv\n";
$postinstall_script .= "ln -s /usr/local/lib/python$python_version/cv.so $python_install_dir/cv.so\n";

$postinstall_script .= "\n#clean up\n";
$postinstall_script .= "rm -r " . $extpkgpath . "\n";

open(PISCRIPT, ">".$buildpath."/post_install.sh");
print PISCRIPT $postinstall_script;
close(PISCRIPT);
