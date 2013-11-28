#!/usr/bin/env python3

from PyQt5 import QtWidgets, QtCore, QtGui
import json
import urllib.request
import random
import sys


class Timer(QtCore.QThread):
    trigger = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.interval = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.tc)

    def setup(self, thread_no=1, interval=0):
        self.thread_no = thread_no
        self.interval = interval

    def run(self):
        self.timer.start(self.interval)

    @QtCore.pyqtSlot()
    def tc(self):
        self.trigger.emit(self.thread_no)


class Window(QtWidgets.QWidget):
    def __init__(self):
        self.TITLE = "BtcChina实时报价"
        self.b = 0
        
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle(self.TITLE)
        self.move(100, 200)
        self.setMinimumSize(500, 500)
        self.setMaximumSize(500, 500)

        self.label1 = QtWidgets.QLabel("Loading...")
        self.label1.setStyleSheet("font-size:50px")
        self.label2 = QtWidgets.QLabel("Loading...")
        self.label2.setStyleSheet("font-size:12px")
        self.label2.setMaximumHeight(60)
        self.label2.setMinimumHeight(60)
        self.graph = Graphs()
        
        # Set Layout
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.label1)
        hbox.addStretch(1)
        hbox.addWidget(self.label2)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.graph)
        self.setLayout(vbox)

        # Start Get Data
        timer = Timer(self)
        timer.trigger.connect(self.setLabel)
        timer.setup(interval=8090)
        timer.start()

    @QtCore.pyqtSlot()
    def setLabel(self):
        a = self.getValue()
        self.label1.setText("￥{0}".format(a["last"]))
        self.label2.setText("High:\t￥{0}\nLow:\t￥{1}\nBuy:\t￥{2}\nSell:\t￥{3}".format(a["high"], a["low"], a["buy"], a["sell"]))
        self.graph.addPoint(a["last"])
        try:
            if a["last"] > self.b:
                self.label1.setStyleSheet("font-size:50px;color:red")
            elif a["last"] < self.b:
                self.label1.setStyleSheet("font-size:50px;color:green")
        except:
            pass
        self.setWindowTitle("￥{0}|{1}".format(a["last"], self.TITLE))
        self.b = a["last"]

    def getValue(self):
        i = random.random()
        url = "http://info.btc123.com/lib/jsonProxyEx.php?type=btcchinaTicker&suffix={0}".format(i)
        try:
            p_conn = urllib.request.urlopen(url)
            b = p_conn.read()
            p_conn.close()
            jso = json.loads(b.decode("utf8"))
            return jso["ticker"]
        except:
            return None

class Graphs(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setMinimumSize(300,300)
        self.isFirst = True
        self.xPrev = self.width() * 0.05
        self.xCur = self.width() * 0.05
        self.valuePrev= self.height()
        self.valueCur = self.height()
        label = QtWidgets.QLabel("10k", self)
        label.move(0,self.height() * 0.03)
        label = QtWidgets.QLabel("0", self)
        label.move(0,self.height() * 0.83)
    
    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawGird(event, painter)
        self.drawFrame(event, painter)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.draw(event, painter)
        painter.end()
    
    def draw(self, event, painter):
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(self.xPrev, self.valuePrev, self.xCur, self.valueCur)

    def drawFrame(self, event, painter):
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawRect(self.width() * 0.05, self.height() * 0.05, self.width() * 0.95, self.height() * 0.95)

    def drawGird(self, event, painter):
        painter.setPen(QtGui.QColor(192, 192, 192))
        for v in range(1, 100):
            painter.drawLine(self.width() * 0.05 * v, self.height() * 0.05, self.width() * 0.05 * v, self.height() )
        for h in range(1, 100):
            painter.drawLine(self.width() * 0.05, self.height() * 0.05 * h, self.width() , self.height() * 0.05 *h)

    def addPoint(self, value):
        self.xPrev = self.xCur
        self.valuePrev = self.valueCur
        if self.xCur >= self.width() * 0.95:
            self.xCur = self.width() * 0.05
            self.xPrev = self.width() * 0.05
            self.valuePrev = self.height()
            self.valueCur = 0
        self.xCur += 10
        value = float(value)
        self.valueCur = int((1.0 - value / 10000) * self.height() * 0.8 + self.height() * 0.05)
        self.update()
        print("DEB:{0}, {1}, {2}, {3}".format(self.xPrev, self.valuePrev, self.xCur, self.valueCur))


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
