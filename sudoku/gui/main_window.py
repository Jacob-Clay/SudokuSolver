"""Main window: owns the board, the menu and the status bar."""

from PySide6.QtGui import QAction, QGuiApplication, QKeySequence
from PySide6.QtWidgets import QInputDialog, QMainWindow, QMessageBox

from sudoku.gui import model_api
from sudoku.gui.board_widget import BoardWidget

EXAMPLE_PUZZLE = "300967001040302080020000070070000090000873000500010003004705100905000207800621004"


class MainWindow(QMainWindow):
    def __init__(self, board=None) -> None:
        super().__init__()
        self.setWindowTitle("Sudoku Solver")
        self.resize(600, 640)

        if board is None:
            board = model_api.board_from_string(EXAMPLE_PUZZLE)
        self.board_widget = BoardWidget(board, self)
        self.setCentralWidget(self.board_widget)
        self.board_widget.message.connect(self._show_message)
        self.board_widget.changed.connect(self._check_solved)

        self._build_menu()
        self.statusBar().showMessage(
            "Click a cell. Digits place, Ctrl+digit toggles a candidate, Delete clears."
        )
        self.board_widget.setFocus()

    def _build_menu(self) -> None:
        puzzle_menu = self.menuBar().addMenu("&Puzzle")
        self._add_action(puzzle_menu, "&Load from string…", QKeySequence.Open, self.load_from_string)
        self._add_action(puzzle_menu, "&Copy as string", "Ctrl+Shift+C", self.copy_as_string)
        self._add_action(puzzle_menu, "&New empty board", QKeySequence.New, self.new_board)
        puzzle_menu.addSeparator()
        self._add_action(puzzle_menu, "&Quit", QKeySequence.Quit, self.close)

        view_menu = self.menuBar().addMenu("&View")
        self._add_action(view_menu, "&Full screen", "F11", self.toggle_full_screen)

    def _add_action(self, menu, text, shortcut, slot) -> QAction:
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    # ---------------------------------------------------------------- actions

    @property
    def board(self):
        return self.board_widget.board

    def load_from_string(self) -> None:
        text, ok = QInputDialog.getText(
            self,
            "Load puzzle",
            "Paste an 81-character puzzle (0 . _ * for blanks):",
        )
        if not ok or not text.strip():
            return
        try:
            board = model_api.board_from_string(text)
        except ValueError as error:
            QMessageBox.warning(self, "Can't load puzzle", str(error))
            return
        self.board_widget.set_board(board)
        self.statusBar().showMessage("Puzzle loaded.", 3000)

    def copy_as_string(self) -> None:
        text = model_api.board_to_string(self.board)
        QGuiApplication.clipboard().setText(text)
        self.statusBar().showMessage("Copied board to clipboard.", 3000)

    def new_board(self) -> None:
        self.board_widget.set_board(model_api.new_board())
        self.statusBar().showMessage("New empty board.", 3000)

    def toggle_full_screen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    # ---------------------------------------------------------------- status

    def _show_message(self, text: str) -> None:
        if text:
            self.statusBar().showMessage(text, 3000)

    def _check_solved(self) -> None:
        if model_api.is_solved(self.board):
            self.statusBar().showMessage("Solved!")
