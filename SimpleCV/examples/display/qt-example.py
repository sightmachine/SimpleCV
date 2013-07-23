#!/usr/bin/env python
'''
This example shows how to display a SimpleCV image in a QT window
the code was taken from the forum post here:
http://help.simplecv.org/question/1866/any-simple-pyqt-sample-regarding-ui-or-display/

Author: Rodrigo gomes 
'''

import os
import sys
import signal
from PyQt4 import uic, QtGui, QtCore
from SimpleCV import *


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(632, 483)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(80, 30, 491, 391))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))


class Webcam(QtGui.QMainWindow):
    def __init__(self, parent=None):

        QtGui.QWidget.__init__(self,parent)        
        self.MainWindow = Ui_Dialog()
        self.MainWindow.setupUi(self)
        self.webcam = Camera(0,{ "width": 640, "height": 480 })

        self.timer = QtCore.QTimer()

        self.connect(self.timer, QtCore.SIGNAL('timeout()'), self.show_frame)

        self.timer.start(1);

    def show_frame(self):
        ipl_image = self.webcam.getImage()
        ipl_image.dl().circle((150, 75), 50, Color.RED, filled = True)
        data = ipl_image.getBitmap().tostring()
        image = QtGui.QImage(data, ipl_image.width, ipl_image.height, 3 * ipl_image.width, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image.rgbSwapped())
        self.MainWindow.label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    webcam = Webcam()
    webcam.show()
    app.exec_()

    
