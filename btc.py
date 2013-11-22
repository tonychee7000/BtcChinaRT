#!/usr/bin/env python3

from PyQt4 import QtGui,QtCore
import json,urllib.request,random,sys


class Label(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setWindowTitle("BtcChina实时报价")
        self.resize(300, 100)
        self.label = QtGui.QLabel("OK")
        self.label.setStyleSheet("font-size:48pt")
        self.setCentralWidget(self.label)
        timer = QtCore.QTimer(self)
        QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("setLabel()"))
        timer.start(8090)

    @QtCore.pyqtSlot()
    def setLabel(self):
        a = self.getValue()
        self.label.setText("￥{0}".format(a))

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
