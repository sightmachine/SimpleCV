#!/usr/bin/perl -w

use strict;
use Cwd qw(getcwd abs_path);
use File::Find qw(find);
use File::Path;
use File::Copy;

#script to take a functional build of simplecv and turn it
#into a file structure appropriate for the mac packagemaker

#first, let's ID all the stuff we homebrew'd
my @homebrew_libs = qw(boost jpeg jasper libfreenect libtiff libusb-freenect little-cms opencv pil tbb);

my @python_libs = qw(cvblob ipython numpy scipy pil matplotlib simplecv);

#check here for compiled cvblob
my $cvblob_location = "/usr/local/lib/libcvblob.dylib";

#look in the current directory, die if it's empty
#a little sad, but i didn't know you could use the diamond operator <> with 
#a path
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

#copy in cvblob, if we have it
if (-e $cvblob_location) {
  copy($cvblob_location, $buildpath . $cvblob_location);
}

#now to get the python libs
my $build_script = abs_path($0);
my ($findmods_path) = $build_script =~ /^(.+)\/[^\/]+$/;
my $findmods_script = $findmods_path . "/findmods.py";
my @pylibs_found = `python $findmods_script`;

foreach my $pylib (@pylibs_found) {
  chomp($pylib);
  my @path_parts = split("/", $pylib);
  my $egg_name = pop(@path_parts);
  foreach my $wantedlib (@python_libs) {
    if ($egg_name =~ /^$wantedlib/i) {
      find( sub {
        next if -d;      
        my $fullpath = $File::Find::name;
        my ($reldir) = $fullpath =~ /^(.+)\/[^\/]+$/;
        my $newdir = $buildpath . $reldir;
        my $newpath = $buildpath . $fullpath;

        if (not -d $newdir) { mkpath($newdir); }
        print "copying $fullpath -> $newpath\n";
        copy($fullpath, $newpath);
        }, $pylib);
    }
  }
}

