arch=$(uname -m)
if [ "$arch" == "i686" -o "$arch" == "i386" -o "$arch" == "i486" -o "$arch" == "i586" ]; then
flag=1
else
flag=0
fi
echo "Installing OpenCV 2.4.2"
mkdir OpenCV
cd OpenCV
echo "Removing any pre-installed ffmpeg and x264"
sudo apt-get remove ffmpeg x264 libx264-dev
echo "Installing Dependenices"
sudo apt-get install libopencv-dev
sudo apt-get install build-essential checkinstall cmake pkg-config yasm
sudo apt-get install libtiff4-dev libjpeg-dev libjasper-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev
sudo apt-get install python-dev python-numpy
sudo apt-get install libtbb-dev
sudo apt-get install libqt4-dev libgtk2.0-dev
echo "Downloading x264"
wget ftp://ftp.videolan.org/pub/videolan/x264/snapshots/x264-snapshot-20120528-2245-stable.tar.bz2
tar -xvf x264-snapshot-20120528-2245-stable.tar.bz2
cd x264-snapshot-20120528-2245-stable/
echo "Installing x264"
if [ $flag -eq 1 ]; then
./configure --enable-static
else
./configure --enable-shared --enable-pic
fi
make
sudo make install
cd ..
echo "Downloading ffmpeg"
wget http://ffmpeg.org/releases/ffmpeg-0.11.1.tar.bz2
echo "Installing ffmpeg"
tar -xvf ffmpeg-0.11.1.tar.bz2
cd ffmpeg-0.11.1/
if [ $flag -eq 1 ]; then
./configure --enable-gpl --enable-libfaac --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid --enable-nonfree --enable-postproc --enable-version3 --enable-x11grab
else
./configure --enable-gpl --enable-libfaac --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid --enable-nonfree --enable-postproc --enable-version3 --enable-x11grab --enable-shared
fi
make
sudo make install
cd ..
echo "Downloading v4l"
wget http://www.linuxtv.org/downloads/v4l-utils/v4l-utils-0.8.8.tar.bz2
echo "Installing v4l"
tar -xvf v4l-utils-0.8.8.tar.bz2
cd v4l-utils-0.8.8/
make
sudo make install
cd ..
echo "Downloading OpenCV 2.4.2"
wget -O OpenCV-2.4.2.tar.bz2 http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.2/OpenCV-2.4.2.tar.bz2/download
echo "Installing OpenCV 2.4.2"
tar -xvf OpenCV-2.4.2.tar.bz2
cd OpenCV-2.4.2
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE ..
make
sudo make install
sudo echo “/usr/local/lib” >> /etc/ld.so.conf
sudo ldconfig
echo "OpenCV 2.4.2 ready to be used"
