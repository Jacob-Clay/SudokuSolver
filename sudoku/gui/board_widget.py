"""Widget that draws a Board and turns mouse/keyboard input into board operations.

Rule: painting only reads the board, it never changes it.
"""

import math

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QWidget

from sudoku.gui import model_api
from sudoku.gui.layout import GridLayout

type Coordinate = tuple[int, int]

# Colours (fixed "paper" look, independent of the system theme)
BACKGROUND = QColor("#f4f1ea")
PAPER = QColor("#ffffff")
LINE = QColor("#1c1c1c")
THIN_LINE = QColor("#9a9a9a")
GIVEN_TEXT = QColor("#1c1c1c")
PLAYER_TEXT = QColor("#1f5fbf")
CANDIDATE_TEXT = QColor("#4a6f9a")
CONFLICT_TEXT = QColor("#c62828")
CONFLICT_FILL = QColor("#fbe3e1")
SELECTED_FILL = QColor("#ffe98a")
SAME_DIGIT_FILL = QColor("#fff6cc")
ERROR_FLASH = QColor("#f4a3a3")

FLASH_MS = 200


class BoardWidget(QWidget):
    """Draws the board and handles input.

    Signals:
        message(str): a short status text, e.g. why a key press was refused.
        changed(): emitted after the board was modified.
    """

    message = Signal(str)
    changed = Signal()

    def __init__(self, board, parent=None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(300, 300)
        self.board = board
        self.selected: Coordinate | None = None
        self._flash: Coordinate | None = None
        self._regions: dict[Coordinate, int] = {}
        self.set_board(board)

    # ------------------------------------------------------------------ state

    def set_board(self, board) -> None:
        self.board = board
        self._regions = model_api.region_lookup(board)
        self.selected = None
        self.update()

    def _layout(self) -> GridLayout:
        n_rows, n_cols = model_api.grid_size(self.board)
        return GridLayout.fit(self.width(), self.height(), n_rows, n_cols)

    # ------------------------------------------------------------------ input

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return
        pos = event.position()
        self.selected = self._layout().cell_at(pos.x(), pos.y())
        self.setFocus()
        self.update()

    def focusNextPrevChild(self, next: bool) -> bool:
        # Keep Tab / Shift+Tab for moving between cells instead of moving focus.
        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        mods = event.modifiers() & ~Qt.KeypadModifier
        # Ctrl on Windows/Linux, Cmd or Ctrl on macOS (Qt maps Cmd to ControlModifier there)
        ctrl = bool(mods & (Qt.ControlModifier | Qt.MetaModifier))

        if key == Qt.Key_Escape:
            self.selected = None
            self.update()
            return

        if self.selected is None:
            if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                self.selected = (0, 0)
                self.update()
            else:
                super().keyPressEvent(event)
            return

        if self._move(key):
            self.update()
            return

        if Qt.Key_1 <= key <= Qt.Key_9:
            digit = key - Qt.Key_0
            if ctrl:
                self._try(model_api.toggle_candidate, digit)
            else:
                self._try(model_api.place, digit)
            return

        if key in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_0):
            self._try(model_api.clear)
            return

        super().keyPressEvent(event)

    def _move(self, key) -> bool:
        """Move the selection for arrow keys / Tab. Returns True if the key was a movement key."""
        n_rows, n_cols = model_api.grid_size(self.board)
        row, col = self.selected
        moves = {
            Qt.Key_Left: (0, -1),
            Qt.Key_Right: (0, 1),
            Qt.Key_Tab: (0, 1),
            Qt.Key_Backtab: (0, -1),
            Qt.Key_Up: (-1, 0),
            Qt.Key_Down: (1, 0),
            Qt.Key_Return: (1, 0),
            Qt.Key_Enter: (1, 0),
        }
        if key not in moves:
            return False
        d_row, d_col = moves[key]
        self.selected = ((row + d_row) % n_rows, (col + d_col) % n_cols)
        return True

    def _try(self, operation, *args) -> None:
        """Run a board operation on the selected cell; show the reason if the board refuses."""
        try:
            operation(self.board, self.selected, *args)
        except ValueError as error:
            self.message.emit(str(error))
            self._flash = self.selected
            QTimer.singleShot(FLASH_MS, self._end_flash)
        else:
            self.message.emit("")
            self.changed.emit()
        self.update()

    def _end_flash(self) -> None:
        self._flash = None
        self.update()

    # --------------------------------------------------------------- painting

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), BACKGROUND)

        layout = self._layout()
        if layout.cell <= 0:
            return
        conflicts = model_api.conflicts(self.board)

        self._paint_backgrounds(painter, layout, conflicts)
        self._paint_thin_lines(painter, layout)
        self._paint_region_borders(painter, layout)
        self._paint_contents(painter, layout, conflicts)

    def _rect(self, layout: GridLayout, coord: Coordinate) -> QRectF:
        return QRectF(*layout.cell_rect(*coord))

    def _cells(self, layout: GridLayout):
        for row in range(layout.n_rows):
            for col in range(layout.n_cols):
                yield (row, col)

    def _paint_backgrounds(self, painter, layout, conflicts) -> None:
        painter.fillRect(QRectF(layout.left, layout.top, layout.width, layout.height), PAPER)

        selected_value = None
        if self.selected is not None:
            selected_value = model_api.get_cell(self.board, self.selected).value

        for coord in self._cells(layout):
            cell = model_api.get_cell(self.board, coord)
            fill = None
            if coord in conflicts:
                fill = CONFLICT_FILL
            if selected_value is not None and cell.value == selected_value:
                fill = SAME_DIGIT_FILL
            if coord == self.selected:
                fill = SELECTED_FILL
            if coord == self._flash:
                fill = ERROR_FLASH
            if fill is not None:
                painter.fillRect(self._rect(layout, coord), fill)

    def _paint_thin_lines(self, painter, layout) -> None:
        painter.setPen(QPen(THIN_LINE, max(1.0, layout.cell * 0.02)))
        right = layout.left + layout.width
        bottom = layout.top + layout.height
        for col in range(1, layout.n_cols):
            x = layout.left + col * layout.cell
            painter.drawLine(x, layout.top, x, bottom)
        for row in range(1, layout.n_rows):
            y = layout.top + row * layout.cell
            painter.drawLine(layout.left, y, right, y)

    def _paint_region_borders(self, painter, layout) -> None:
        """Thick line wherever two neighbouring cells are in different regions.

        Works for any region shape, so jigsaw layouts draw correctly too.
        """
        pen = QPen(LINE, max(2.0, layout.cell * 0.06))
        pen.setCapStyle(Qt.SquareCap)
        painter.setPen(pen)
        for row, col in self._cells(layout):
            x, y, size, _ = layout.cell_rect(row, col)
            region = self._regions.get((row, col))
            if col + 1 < layout.n_cols and self._regions.get((row, col + 1)) != region:
                painter.drawLine(x + size, y, x + size, y + size)
            if row + 1 < layout.n_rows and self._regions.get((row + 1, col)) != region:
                painter.drawLine(x, y + size, x + size, y + size)

        painter.setBrush(Qt.NoBrush)
        painter.drawRect(QRectF(layout.left, layout.top, layout.width, layout.height))

    def _paint_contents(self, painter, layout, conflicts) -> None:
        digit_font = QFont()
        digit_font.setPixelSize(max(1, int(layout.cell * 0.62)))
        candidate_font = QFont()
        candidate_font.setPixelSize(max(1, int(layout.cell * 0.24)))

        for coord in self._cells(layout):
            cell = model_api.get_cell(self.board, coord)
            rect = self._rect(layout, coord)

            if cell.value is not None:
                digit_font.setBold(cell.given)
                painter.setFont(digit_font)
                if coord in conflicts:
                    painter.setPen(CONFLICT_TEXT)
                elif cell.given:
                    painter.setPen(GIVEN_TEXT)
                else:
                    painter.setPen(PLAYER_TEXT)
                painter.drawText(rect, Qt.AlignCenter, str(cell.value))
            elif cell.candidates:
                painter.setFont(candidate_font)
                painter.setPen(CANDIDATE_TEXT)
                self._paint_candidates(painter, rect, cell.candidates, layout.n_cols)

    def _paint_candidates(self, painter, rect: QRectF, candidates, max_digit: int) -> None:
        """Each digit in a fixed spot: 1 top-left ... 9 bottom-right."""
        per_row = math.ceil(math.sqrt(max_digit))
        n_rows = math.ceil(max_digit / per_row)
        pad = rect.width() * 0.06
        sub_w = (rect.width() - 2 * pad) / per_row
        sub_h = (rect.height() - 2 * pad) / n_rows
        for digit in sorted(candidates):
            index = digit - 1
            sub = QRectF(
                rect.left() + pad + (index % per_row) * sub_w,
                rect.top() + pad + (index // per_row) * sub_h,
                sub_w,
                sub_h,
            )
            painter.drawText(sub, Qt.AlignCenter, str(digit))
