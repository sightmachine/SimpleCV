#!/usr/bin/perl -w

use strict;
use Cwd qw(getcwd abs_path);
use File::Find qw(find);
use File::Path;
use File::Copy;
use File::Fetch;

#script to take a functional build of simplecv and turn it
#into a file structure appropriate for the mac packagemaker
my $python_version = 2.6;
my $python_install_dir = "/Library/Python/$python_version/site-packages/";

#first, let's ID all the stuff we homebrew'd
my @homebrew_libs = qw(jpeg jasper libfreenect libtiff libusb-freenect little-cms opencv pil tbb);

#where the most recent/appropriate version of easy install is
my $easyinstall_location = "http://pypi.python.org/packages/$python_version/s/setuptools/setuptools-0.6c11-py$python_version.egg";

#what packages we need to postinstall
my @pkgs = qw(
  http://r.research.att.com/gfortran-42-5664.pkg
  http://f0o.com/~rene/stuff/pygame-1.9.2pre-py2.6-macosx10.6.mpkg.zip
);

#the python libs we're going to bundle and easyinstall
my @python_libs = qw(
  http://dl.dropbox.com/u/233041/PyMC/numpy-2.0.0.dev_3071eab_20110527-py2.6-macosx-10.6-universal.egg
  http://dl.dropbox.com/u/233041/PyMC/scipy-0.10.0.dev_20110527-py2.6-macosx-10.6-universal.egg
  http://ipython.scipy.org/dist/0.10.2/ipython-0.10.2-py2.6.egg
  http://sourceforge.net/projects/simplecv/files/1.1/SimpleCV-1.1.tar.gz
);

my $examples_url = "http://sourceforge.net/projects/simplecv/files/1.1/SimpleCV_examples-1.1.zip";



my @python_lib_manual = qw(
  http://ingenuitas.com/shared/freenect-python-0.0.0.tar.gz
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
    `cp $fullpath $newpath`;
    print "copying $fullpath -> $newpath \n";
    }, $version_path);
}

#now to get the remaining external packages 
my $extpkgpath = "/var/tmp/simplecv";
my $buildpkgpath = $buildpath . $extpkgpath;
mkpath($buildpkgpath);

my $postinstall_script = "#!/bin/sh\ncd $extpkgpath\n";

sub fetchPackage {
  my ($pkg_url) = @_;
  my $ff = File::Fetch->new(uri => $pkg_url);
  my $where = $ff->fetch( to => $buildpkgpath );
  return $ff->output_file;
}

my $easyinstall_fname = fetchPackage($easyinstall_location);
$postinstall_script .= "\n#install easy_install\n";
$postinstall_script .= "./$easyinstall_fname\n";

$postinstall_script .= "\n#install external pkgs\n";
foreach my $pkg (@pkgs) {
  my $pkg_fname = fetchPackage($pkg);
  if ($pkg_fname =~ /zip$/) {
    $postinstall_script .= "sudo unzip $pkg_fname\n";
    $pkg_fname =~ s/\.zip$//g;
  }
  $postinstall_script .= "sudo installer -pkg '$pkg_fname' -target '/'\n";
}

$postinstall_script .= "\n#install python deps\n";
foreach my $pylib (@python_libs) {
  my $pkg_fname = fetchPackage($pylib);
  $postinstall_script .= "ARCHFLAGS='-arch i386 -arch x86_64' easy_install $pkg_fname\n";
}

$postinstall_script .= "\n#install manual python deps\n";
foreach my $manuallib (@python_lib_manual) {
  my $pkg_fname = fetchPackage($manuallib);
  $postinstall_script .= "tar xzf $pkg_fname -C $python_install_dir\n";
}

$postinstall_script .= "\n#and finally, symlink opencv\n";
$postinstall_script .= "ln -s /usr/local/lib/python$python_version/site-packages/cv.so $python_install_dir/cv.so\n";
$postinstall_script .= "ln -s /usr/local/lib/python$python_version/site-packages/PIL $python_install_dir/PIL\n";

$postinstall_script .= "\n#clean up\n";
$postinstall_script .= "sudo rm -r " . $extpkgpath . "\n";

my $piscript = $buildpkgpath . "/post_install.command";
open(PISCRIPT, ">$piscript");
print PISCRIPT $postinstall_script;
close(PISCRIPT);
chmod(0755, $piscript);

my $cmd = <<SIMPLECV_COMMAND;
#!/usr/bin/python
from SimpleCV import *
from SimpleCV.Shell import *
main()
SIMPLECV_COMMAND

my $appdir = $buildpath . "/Applications/SimpleCV";
mkpath($appdir);
my $cmdfile = $appdir . "/SimpleCV.command";
open CMDFILE, ">$cmdfile";
print CMDFILE $cmd;
close CMDFILE;
chmod(0755, $cmdfile);


my $ff = File::Fetch->new(uri => $examples_url);
my $where = $ff->fetch( to => $appdir );
chdir($appdir);
`unzip $where`;
`rm $where`;

chdir($buildpath);
`chown -R root:staff usr`;
`chmod -R ug+w usr`;
`chmod -R a+rwx var/tmp`; 
