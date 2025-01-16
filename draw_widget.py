import bisect

from PySide6.QtWidgets import ( 
    QWidget,
)
from PySide6.QtGui import (
    QKeyEvent, 
    QMouseEvent,
    QPainter, 
    QPen, 
    QFont, 
)
from PySide6.QtCore import (
    Qt, 
    QRect
)

NUM_BOXES_X = 9
NUM_BOXES_Y = 9

class DrawWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.data = [[{} for _ in range(NUM_BOXES_Y)] for _ in range(NUM_BOXES_X)]
        self.numBoxes_x = NUM_BOXES_X
        self.numBoxes_y = NUM_BOXES_Y
        self.point = None
        self.square = None
        self.clipboard = None
        self.previous_geometry = None

        self.setFocusPolicy(Qt.StrongFocus)

        self.regions = [
            [
                [0, 0], [0, 1], [0, 2],
                [1, 0], [1, 1], [1, 2],
                [2, 0], [2, 1], [2, 2]
            ],
            [
                [0, 3], [0, 4], [0, 5],
                [1, 3], [1, 4], [1, 5],
                [2, 3], [2, 4], [2, 5]
            ],
            [
                [0, 6], [0, 7], [0, 8],
                [1, 6], [1, 7], [1, 8],
                [2, 6], [2, 7], [2, 8]
            ],
            [
                [3, 0], [3, 1], [3, 2],
                [4, 0], [4, 1], [4, 2],
                [5, 0], [5, 1], [5, 2]
            ],
            [
                [3, 3], [3, 4], [3, 5],
                [4, 3], [4, 4], [4, 5],
                [5, 3], [5, 4], [5, 5]
            ],
            [
                [3, 6], [3, 7], [3, 8],
                [4, 6], [4, 7], [4, 8],
                [5, 6], [5, 7], [5, 8]
            ],
            [
                [6, 0], [6, 1], [6, 2],
                [7, 0], [7, 1], [7, 2],
                [8, 0], [8, 1], [8, 2]
            ],
            [
                [6, 3], [6, 4], [6, 5],
                [7, 3], [7, 4], [7, 5],
                [8, 3], [8, 4], [8, 5]
            ],
            [
                [6, 6], [6, 7], [6, 8],
                [7, 6], [7, 7], [7, 8],
                [8, 6], [8, 7], [8, 8]
            ]
        ]

    def update_data(self, data):
        self.data = data
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.black, 5, Qt.SolidLine)
        painter.setPen(pen)

        width = self.width()
        height = self.height()
        minimum_size = min(width, height)
        
        step = minimum_size / (self.numBoxes_x + 2)
        maxSide_x = step + (self.numBoxes_x * step)
        maxSide_y = step + (self.numBoxes_y * step)

        self.checkDoubles()

        self.drawBoundaries(maxSide_x, maxSide_y, step, painter, pen)

        self.drawSelectedBox(maxSide_x, maxSide_y, step, painter, pen)

        self.drawText(maxSide_x, maxSide_y, step, painter, pen)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            pos = event.position()
            self.point = (pos.x(), pos.y())
            self.update() 

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if self.square == None:
            return
        key_combo = event.keyCombination()
        if key_combo.keyboardModifiers() != Qt.NoModifier and key_combo.keyboardModifiers() != Qt.KeypadModifier:
            self.checkModified(event)
            return
        i = self.square[0]
        j = self.square[1]
        key = event.key()
        if Qt.Key_0 <= key <= Qt.Key_9:
            if self.data[i][j] == {} or self.data[i][j]["given"] == False:
                self.data[i][j] = {"given": False, "value": self.keyToNum(key)}
        elif Qt.Key_Backspace == key or key == Qt.Key_Delete:
            self.data[i][j] = {}
        elif Qt.Key_Left == key:
            self.square = ((i - 1) % self.numBoxes_x, j)
        elif Qt.Key_Right == key or Qt.Key_Tab == key:
            self.square = ((i + 1) % self.numBoxes_x, j)
        elif Qt.Key_Up == key:
            self.square = (i, (j - 1) % self.numBoxes_y)
        elif Qt.Key_Down == key or Qt.Key_Return == key or Qt.Key_Enter == key:
            self.square = (i, (j + 1) % self.numBoxes_y)
        elif Qt.Key_Escape == key:
            self.square = None
        elif Qt.Key_F11 == key: #specifically this one key has issues
            if self.previous_geometry == None:
                self.previous_geometry = self.parentWidget().geometry()
                self.parentWidget().showMaximized()
            else:
                current_geometry = self.parentWidget().geometry()
                self.parentWidget().setGeometry(self.previous_geometry)
                self.previous_geometry = current_geometry
        self.update()
    
    def keyToNum(self, key: Qt.Key) -> str:
        if Qt.Key_0 == key:
            return "0"
        if Qt.Key_1 == key:
            return "1"
        if Qt.Key_2 == key:
            return "2"
        if Qt.Key_3 == key:
            return "3"
        if Qt.Key_4 == key:
            return "4"
        if Qt.Key_5 == key:
            return "5"
        if Qt.Key_6 == key:
            return "6"
        if Qt.Key_7 == key:
            return "7"
        if Qt.Key_8 == key:
            return "8"
        if Qt.Key_9 == key:
            return "9"
        return ""

    def checkModified(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()
        i = self.square[0]
        j = self.square[1]

        if modifiers == Qt.ControlModifier or modifiers == Qt.ControlModifier|Qt.KeypadModifier:
            if key == Qt.Key_C:
                self.clipboard = self.data[self.square[0]][self.square[1]].copy()
                if self.clipboard != {}:
                    self.clipboard["given"] = False
            if key == Qt.Key_V:
                self.data[self.square[0]][self.square[1]] = self.clipboard
                self.update() 
            if Qt.Key_0 <= key <= Qt.Key_9:
                cell = self.data[i][j]
                if cell == {} or cell["given"] == False:
                    num = self.keyToNum(key)
                    if cell != {} and "centermarks" in cell:
                        if num in cell["centermarks"]:
                            self.data[i][j]["centermarks"].remove(num)
                        else:
                            position = bisect.bisect(cell["centermarks"], num)
                            self.data[i][j]["centermarks"].insert(position, num)
                    else:
                        self.data[i][j] = {"given": False, "centermarks": [num]}
                    self.update()
        elif modifiers == Qt.ShiftModifier:
            if key == Qt.Key_Backtab:
                self.square = ((self.square[0] - 1) % self.numBoxes, self.square[1])
                self.update()


    def drawBoundaries(self, maxSide_x, maxSide_y, step, painter: QPainter, pen: QPen):
        
        painter.drawRect(step, step, maxSide_x - step, maxSide_y - step)
        pen.setWidth(2)
        painter.setPen(pen)
        # basic lines making the grid
        for i in range(1, self.numBoxes_x):
            painter.drawLine(step+(step*i), step, step+(step*i), maxSide_y)
        for i in range(1, self.numBoxes_y):
            painter.drawLine(step, step+(step*i), maxSide_x, step+(step*i))
        
        # painter.drawLine(x1, y1, x2, y2)

        pen.setWidth(4)
        painter.setPen(pen)

        for region in self.regions:
            seen_x = set()
            seen_y = set()  
            for cell in region:
                if cell[0] not in seen_x:
                    seen_x.add(cell[0])
                if cell[1] not in seen_y:
                    seen_y.add(cell[1])
        
            start_x = (min(seen_x) + 1) * step
            start_y = (min(seen_y) + 1) * step
            length_x = len(seen_x) * step
            length_y = len(seen_y) * step

            painter.drawRect(start_x, start_y, length_x, length_y)

    def drawText(self, maxSide_x, maxSide_y, step, painter: QPainter, pen: QPen):
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                self.drawCellContents(maxSide_x, maxSide_y, step, painter, pen, i, j)
    

    def drawCellContents(self, maxSide_x, maxSide_y, step, painter: QPainter, pen: QPen, i, j) -> None:
        """
        Draws the text within the cell.
        
        Parameters:
        step (float): the length of a side of a cell.
        painter (QPainter): the painter object used to draw.
        pen (QPen): the pen object used to draw.
        i (int): the row index of the cell.
        j (int): the column index of the cell.
        """
        # Get cell data and if it is empty, return
        cell = self.data[i][j]
        if cell == {}:
            return
        
        # Set up the font
        screen = self.window().windowHandle().screen()
        font_resolution = screen.logicalDotsPerInch()
        font = QFont()
        font.setFamily("Arial")
        font.setWeight(QFont.Bold)
        
        # Determine pen color
        if cell.get("given", False) and "value" in cell:
            pen.setColor(Qt.black)
        elif cell.get("double", False): 
            pen.setColor(Qt.red)
        else:
            pen.setColor(Qt.blue)
        painter.setPen(pen)

        # If the cell is a given or does not have centermarks, draw the number
        if cell.get("given", False) or "centermarks" not in cell:
            num = cell.get("value", "")
            font_size_in_dip = step / 1.25
            font.setPixelSize(int(font_size_in_dip * (font_resolution / 96.0)))
            painter.setFont(font)

            # Define the text rectangle and draw the text
            cell_center_x = (i + 1.5) * step
            cell_center_y = (j + 1.5) * step
            buffer = step * 0.1
            text_rect = QRect(
                cell_center_x - (step / 2) + buffer,
                cell_center_y - (step / 2) + buffer, 
                step - (2 * buffer), 
                step - (2 * buffer)
            )
            painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, num)
            return
        
        # If the cell has centermarks, handle each centermark separately
        if "centermarks" not in cell or len(cell["centermarks"]) == 0:
            return
        centermarks = cell.get("centermarks", [])
        max_marks_per_row = 3  # Adjust this for layout
        rows = (len(centermarks) + max_marks_per_row - 1) // max_marks_per_row
        font_size_in_dip = step / (3.75 if len(centermarks) > 6 else 3)
        font.setPixelSize(int(font_size_in_dip * (font_resolution / 96.0)))
        painter.setFont(font)

        # Define starting point for centermarks
        cell_center_x = (i + 1.5) * step
        cell_center_y = (j + 1.5) * step
        text_width = step / max_marks_per_row
        text_height = step / rows

        for idx, mark in enumerate(centermarks):
            # Determine position for the current mark
            row = idx // max_marks_per_row
            col = idx % max_marks_per_row
            mark_x = cell_center_x - step / 2 + col * text_width + text_width / 2
            mark_y = cell_center_y - step / 2 + row * text_height + text_height / 2

            # Set pen color for the specific mark
            if mark in cell.get("double_centermarks", []):
                pen.setColor(Qt.red)
            else:
                pen.setColor(Qt.blue)
            painter.setPen(pen)

            # Draw the centermark
            painter.drawText(
                QRect(
                    mark_x - text_width / 2,
                    mark_y - text_height / 2,
                    text_width,
                    text_height,
                ),
                Qt.AlignCenter,
                mark
            )


    def drawSelectedBox(self, maxSide_x, maxSide_y, step, painter: QPainter, pen: QPen):
        """draws the box around the selected cell"""
        if self.point != None:
            if self.point[0] < step or self.point[1] < step or self.point[0] > maxSide_x or self.point[1] > maxSide_y:
                self.point = None
                self.square = None
            else:
                point_x = self.point[0]
                point_y = self.point[1]
                start_x = 0
                start_y = 0
                for i in range(1, self.numBoxes_x):
                    if point_x < step + (i * step):
                        break
                    start_x = i
                for i in range(1, self.numBoxes_y):
                    if point_y < step + (i * step):
                        break
                    start_y = i

                pen.setColor(Qt.red)
                painter.setPen(pen)
                painter.drawRect(step + (start_x * step), step + (start_y * step), step, step)
                self.point = None
                self.square = (start_x, start_y)
        elif self.square != None:
            start_x = self.square[0]
            start_y = self.square[1]
            pen.setColor(Qt.red)
            painter.setPen(pen)
            painter.drawRect(step + (start_x * step), step + (start_y * step), step, step)


    """
    Actually start solving stuff rather than just drawing
    """
    def resetDoubles(self):
        for i in range(self.numBoxes_x):
            for j in range(self.numBoxes_y):
                cell = self.data[i][j]
                if cell == {}:
                    continue
                cell["double"] = False
                cell["double_centermarks"] = []


    def checkDoubles(self):
        self.resetDoubles()
        horizontal_value_to_cell_dict = {}
        vertical_value_to_cell_dict = {}
        regionial_value_to_cell_dict = {}

        for i in range(self.numBoxes_x):
            for j in range(self.numBoxes_y):
                cell = self.data[i][j]

                if cell == {} or "value" not in cell:
                    continue

                cell_value = cell["value"]
                # check horizontal
                if i not in horizontal_value_to_cell_dict:
                    horizontal_value_to_cell_dict[i] = {}
                if cell_value in horizontal_value_to_cell_dict.get(i, {}):
                    other_cell = horizontal_value_to_cell_dict[i][cell_value]
                    self.data[i][j]["double"] = True
                    self.data[other_cell[0]][other_cell[1]]["double"] = True
                else:
                    horizontal_value_to_cell_dict[i][cell_value] = (i, j)
                
                # check vertical
                if j not in vertical_value_to_cell_dict:
                    vertical_value_to_cell_dict[j] = {}
                if cell_value in vertical_value_to_cell_dict.get(j, {}):
                    other_cell = vertical_value_to_cell_dict[j][cell_value]
                    self.data[i][j]["double"] = True
                    self.data[other_cell[0]][other_cell[1]]["double"] = True
                else:
                    vertical_value_to_cell_dict[j][cell_value] = (i, j)

                # check regions
                region = (i // 3) * 3 + (j // 3)
                if region not in regionial_value_to_cell_dict:
                    regionial_value_to_cell_dict[region] = {}
                if cell_value in regionial_value_to_cell_dict.get(region, {}):
                    other_cell = regionial_value_to_cell_dict[region][cell_value]
                    self.data[i][j]["double"] = True
                    self.data[other_cell[0]][other_cell[1]]["double"] = True
                else:
                    regionial_value_to_cell_dict[region][cell_value] = (i, j)

        ## check for doubles in centermarks
        for i in range(self.numBoxes_x):
            for j in range(self.numBoxes_y):
                cell = self.data[i][j]
                if "centermarks" not in cell:
                    continue

                for centermark in cell["centermarks"]:
                    # check horizontal
                    if centermark in horizontal_value_to_cell_dict.get(i, {}):
                        self.data[i][j]["double_centermarks"].append(centermark)
                    # check vertical
                    if centermark in vertical_value_to_cell_dict.get(j, {}):
                        self.data[i][j]["double_centermarks"].append(centermark)
                    # check regions
                    region = (i // 3) * 3 + (j // 3)
                    if centermark in regionial_value_to_cell_dict.get(region, {}):
                        self.data[i][j]["double_centermarks"].append(centermark)
