#!/usr/bin/env python3
#
# Copyright (C) 2013 - Tony Chyi <tonychee1989@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.

from PyQt5 import QtWidgets, QtCore, QtGui
import json
import urllib.request
import sys


class Timer(QtCore.QThread):
    """Run QTimer in another thread."""

    trigger = QtCore.pyqtSignal(int, dict)

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
        try:
            val = self.getValue()
            self.trigger.emit(self.thread_no, val)
        except TypeError as err:
            print('\033[31;1mERR:\033[0m', err)

    def getValue(self):
        """This is used for get json from specified address."""

        url = "https://data.btcchina.com/data/ticker"
        try:
            p_conn = urllib.request.urlopen(url)
            b = p_conn.read()
            p_conn.close()
            jso = json.loads(b.decode("utf8"))
            return jso["ticker"]
        except:
            return None



class Window(QtWidgets.QWidget):
    def __init__(self):
        self.TITLE = "BtcChina实时报价"
        self.valPrev = 0

        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle(self.TITLE)
        self.move(100, 200)
        self.setMinimumSize(500, 500)
        self.setMaximumSize(500, 500)

        # Get ready for widget
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
        timer.setup(interval=10000)
        timer.start()

    @QtCore.pyqtSlot(int, dict)
    def setLabel(self, thread_no, val):
        try:
            self.label1.setText("￥{0}".format(val["last"]))
            self.label2.setText("High:\t￥{0}\nLow:\t￥{1}\nBuy:\t￥{2}\nSell:\t￥{3}".format(val["high"], val["low"], val["buy"], val["sell"]))
            self.graph.setPeak(val["high"], val["low"])
            self.graph.addPoint(val["last"])
            if float(val["last"]) > self.valPrev:
                self.label1.setStyleSheet("font-size:50px;color:red")  # WOW! Bull market!
            elif float(val["last"]) < self.valPrev:
                self.label1.setStyleSheet("font-size:50px;color:green")  # Damn bear market!
            self.setWindowTitle("￥{0}|{1}".format(val["last"], self.TITLE))
            self.valPrev = float(val["last"])
        except:
            pass


class Graphs(QtWidgets.QWidget):
    """A costomized controller, to show graph on the window."""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.flagFirst = True
        self.setMinimumSize(300, 300)
        self.recentData = []  # To draw lines, a list is needed
        self.max_ = 10000
        self.min_ = 0
        self.valuePrev = self.height()
        self.mousePosit = QtCore.QPoint(0, 0)
        self.label1 = QtWidgets.QLabel("10k", self)
        self.label1.move(0, self.height() * 0.03)
        self.label2 = QtWidgets.QLabel("0", self)
        self.label2.move(0, self.height() * 0.83)
        self.setStep(10)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawGird(event, painter)
        self.drawFrame(event, painter)
        self.drawMouse(event, painter)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.draw(event, painter)
        painter.end()

    def draw(self, event, painter):
        """Draw data line on widget."""

        pen = QtGui.QPen(QtGui.QColor(0, 0, 0), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)
        xPrev = self.width() * 0.10
        xCur = self.width() * 0.10
        for value in self.recentData:
            xCur += self.step
            painter.drawLine(xPrev, self.valuePrev, xCur, value)
            self.valuePrev = value
            xPrev = xCur

    def drawFrame(self, event, painter):
        """Draw the border of chart."""

        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawRect(self.width() * 0.10, self.height() * 0.05, self.width() * 0.90, self.height() * 0.95)

    def drawGird(self, event, painter):
        """Draw gird on chart"""

        painter.setPen(QtGui.QColor(192, 192, 192))
        for v in range(2, 100):
            painter.drawLine(self.width() * 0.05 * v, self.height() * 0.05, self.width() * 0.05 * v, self.height())
        for h in range(1, 100):
            painter.drawLine(self.width() * 0.10, self.height() * 0.05 * h, self.width(), self.height() * 0.05 * h)

    def drawMouse(self, event, painter):
        if self.mousePosit in QtCore.QRect(self.width() * 0.1, self.height() * 0.05, self.width() * 0.9, self.height() * 0.95):
            painter.setPen(QtGui.QColor(255, 0, 255))
            painter.drawLine(self.mousePosit.x(), self.height() * 0.05, self.mousePosit.x(), self.height())
            painter.drawLine(self.width() * 0.10, self.mousePosit.y(), self.width(), self.mousePosit.y())
            price = float((1 - (self.mousePosit.y() - self.height() * 0.05) / (self.height() * 0.95)) * (self.max_ - self.min_) + self.min_)
            painter.setPen(QtGui.QColor(0, 0, 255))
            painter.drawText(QtCore.QPoint(self.width() * 0.1, self.mousePosit.y()), format(price, '.2f'))

    def addPoint(self, value):
        """Append a data to data list, for drawing lines."""

        value = float(value)
        valueCur = int((1.0 - (value - self.min_) / (self.max_ - self.min_)) * self.height() * 0.95 + self.height() * 0.05)
        self.recentData.append(valueCur)
        if len(self.recentData) >= self.posit:
            del self.recentData[0]  # Del the first data, look like the chart moving.
        self.update()

    def setPeak(self, max_, min_):
        """Set the max/min value of the chart."""

        self.max_ = float(max_)
        self.min_ = float(min_)
        self.label1.setText(max_)
        self.label1.adjustSize()
        self.label2.setText(min_)
        self.label2.adjustSize()
        self.update()

    def setStep(self, step):
        """Set the length of X to a line."""

        step = int(step)
        self.step = step
        self.posit = len(range(int(self.width() * 0.10), int(self.width() * 0.75), step))

    def mouseMoveEvent(self, event):
        self.mousePosit = event.pos()
        self.update()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
