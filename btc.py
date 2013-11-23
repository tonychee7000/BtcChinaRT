#!/usr/bin/env python3

from PyQt4 import QtGui, QtCore
import json
import urllib.request
import random
import sys

class Timer(QtCore.QThread):
    trigger = QtCore.pyqtSignal(int)
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.interval = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tc)

    def setup(self, thread_no = 1, interval = 0):
        self.thread_no = thread_no
        self.interval = interval
    
    def run(self):
        self.timer.start(self.interval)

    @QtCore.pyqtSlot()
    def tc(self):
        self.trigger.emit(self.thread_no)
        

class Label(QtGui.QMainWindow):
    def __init__(self):
        self.TITLE = "BtcChina实时报价"
        QtGui.QWidget.__init__(self)
        self.setWindowTitle(self.TITLE)
        self.move(100, 200)
        self.resize(300, 100)
        self.label = QtGui.QLabel("Loading...")
        self.label.setStyleSheet("font-size:48pt")
        self.setCentralWidget(self.label)
        self.b = 0
        timer = Timer(self)
        timer.trigger.connect(self.setLabel)
        timer.setup(interval = 8090)
        timer.start()

    @QtCore.pyqtSlot()
    def setLabel(self):
        a = self.getValue()
        self.label.setText("￥{0}".format(a))
        try:
            if a > self.b:
                self.label.setStyleSheet("font-size:48pt;color:red")
            elif a < self.b:
                self.label.setStyleSheet("font-size:48pt;color:green")
        except:
            pass
        self.setWindowTitle("￥{0}|{1}".format(a, self.TITLE))
        self.b = a

    def getValue(self):
        i = random.random()
        url = "http://info.btc123.com/lib/jsonProxyEx.php?type=btcchinaTicker&suffix={0}".format(i)
        try:
            p_conn = urllib.request.urlopen(url)
            b = p_conn.read()
            p_conn.close()
            jso = json.loads(b.decode("utf8"))
            return jso["ticker"]["last"]
        except:
            return "null"


def main():
    app = QtGui.QApplication(sys.argv)
    label = Label()
    label.show()
    app.exec_()

if __name__ == "__main__":
    main()
