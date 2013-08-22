arch=$(uname -m)
if [ "$arch" == "i686" -o "$arch" == "i386" -o "$arch" == "i486" -o "$arch" == "i586" ]; then
flag=1
else
flag=0
fi
echo "Installing OpenCV 2.4.5"
mkdir OpenCV
cd OpenCV
echo "Removing any pre-installed ffmpeg and x264"
apt-get -y remove ffmpeg x264 libx264-dev
echo "Installing Dependenices"
apt-get -y install libopencv-dev
apt-get -y install build-essential checkinstall cmake pkg-config yasm
apt-get -y install libtiff4-dev libjpeg-dev libjasper-dev
apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev
apt-get -y install python-dev python-numpy
apt-get -y install libtbb-dev
apt-get -y install libqt4-dev libgtk2.0-dev
apt-get -y install libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev
apt-get -y install x264 v4l-utils ffmpeg
echo "Downloading OpenCV 2.4.5"
wget -O OpenCV-2.4.5.tar.gz http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.5/opencv-2.4.5.tar.gz/download
echo "Installing OpenCV 2.4.5"
tar -xvf OpenCV-2.4.5.tar.gz
cd opencv-2.4.5
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON -D WITH_QT=ON -D WITH_OPENGL=ON ..
make -j4
make install
sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
ldconfig
echo "OpenCV 2.4.5 ready to be used"
