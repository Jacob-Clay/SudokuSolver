import sys
import random
# from PySide6 import QtCore, QtWidgets, QtGui

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout
from PySide6.QtGui import QKeyEvent, QPainter, QPen, QFont, QScreen
from PySide6.QtCore import Qt, Slot

NUM_BOXES = 9

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TESTING!")
        self.setGeometry(100, 100, 550, 550)
        # self.setGeometry(x, y, w, h)

        central_widget = DrawWidget()
        self.setCentralWidget(central_widget)


class DrawWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = [["0" for _ in range(NUM_BOXES)] for _ in range(NUM_BOXES)]
        self.numBoxes = NUM_BOXES
        self.point = None
        self.square = None

        self.setFocusPolicy(Qt.StrongFocus)

    def update_data(self, data):
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.black, 4, Qt.SolidLine)
        painter.setPen(pen)

        width = self.width()
        height = self.height()
        minimum_size = min(width, height)
        # because we are drawing a square i can ignore differences in x and y
        step = minimum_size / (self.numBoxes + 2)
        minSide = step
        maxSide = minSide + (self.numBoxes * step)

        self.drawBoundaries(minSide, maxSide, step, painter, pen)

        self.drawText(minSide, maxSide, step, painter, pen)

        self.drawSelectedBox(minSide, maxSide, step, painter, pen)
        
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position()
            self.point = (pos.x(), pos.y())
            self.update()

    def keyPressEvent(self, event):
        if self.square == None:
            return
        i = self.square[0]
        j = self.square[1]
        if Qt.Key_0 <= event.key() <= Qt.Key_9:
            self.data[i][j] = event.text()

            self.update()
        elif Qt.Key_Backspace == event.key() or event.key() == Qt.Key_Delete:
            self.data[i][j] = "0"
            self.update()
        elif Qt.Key_Left == event.key():
            self.square = (max(0, i-1), j)
            self.update()
        elif Qt.Key_Right == event.key() or Qt.Key_Tab == event.key():
            self.square = (min(self.numBoxes, i+1), j)
            self.update()
        elif Qt.Key_Up == event.key():
            self.square = (i, max(0, j-1))
            self.update()
        elif Qt.Key_Down == event.key() or Qt.Key_Return == event.key() or Qt.Key_Enter == event.key():
            self.square = (i, min(self.numBoxes, j+1))
            self.update()

    def drawBoundaries(self, minSide, maxSide, step, painter, pen):
        
        painter.drawRect(minSide, minSide, maxSide - minSide, maxSide - minSide)

        for i in range(1, self.numBoxes):
            if (i == 3 or i == 6):
                pen.setWidth(3)
                painter.setPen(pen)
            else:
                pen.setWidth(2)
                painter.setPen(pen)
            painter.drawLine(minSide+(step*i), minSide, minSide+(step*i), maxSide)
            painter.drawLine(minSide, minSide+(step*i), maxSide, minSide+(step*i))


    def drawText(self, minSide, maxSide, step, painter, pen):
        screen = self.window().windowHandle().screen()
        font_resolution = screen.logicalDotsPerInch()
        font_size_in_dip = step / 1.25 # change this as desired
        font = QFont()
        font.setFamily("Arial")
        font.setWeight(QFont.Bold)
        font.setPixelSize(int(font_size_in_dip * (font_resolution / 96.0)))

        painter.setFont(font)
        first_center = step + (step / 2)
        # I want to write in the middle of the square so I am doing it like this
        
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                num = self.data[i][j]
                if num == "0":
                    continue
                text_rect = painter.fontMetrics().boundingRectChar(num)

                text_x = first_center - (text_rect.width() / 2) + (i * step)
                text_y = first_center + (text_rect.height() / 2) + (j * step)

                painter.drawText(text_x, text_y, num)



    def drawSelectedBox(self, minSide, maxSide, step, painter, pen):
        if self.point != None:
            if self.point[0] < minSide or self.point[1] < minSide or self.point[0] > maxSide or self.point[1] > maxSide:
                self.point = None
                self.square = None
            else:
                point_x = self.point[0]
                point_y = self.point[1]
                start_x = 0
                start_y = 0
                for i in range(1, self.numBoxes):
                    if point_x < minSide + (i * step):
                        break
                    start_x = i
                for i in range(1, self.numBoxes):
                    if point_y < minSide + (i * step):
                        break
                    start_y = i

                pen.setColor(Qt.red)
                painter.setPen(pen)
                painter.drawRect(minSide + (start_x * step), minSide + (start_y * step), step, step)
                self.point = None
                self.square = (start_x, start_y)
        elif self.square != None:
            start_x = self.square[0]
            start_y = self.square[1]
            pen.setColor(Qt.red)
            painter.setPen(pen)
            painter.drawRect(minSide + (start_x * step), minSide + (start_y * step), step, step)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())