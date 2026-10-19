"""Main window: owns the board, the menu and the status bar."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence
from PySide6.QtWidgets import QApplication, QInputDialog, QMainWindow, QMessageBox

from sudoku.gui import model_api
from sudoku.gui.board_widget import BoardWidget

EXAMPLE_PUZZLE = (
    "300967001040302080020000070070000090000873000500010003004705100905000207800621004"
)


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
        self._add_action(
            puzzle_menu, "&Load from string…", QKeySequence.Open, self.load_from_string
        )
        self._add_action(
            puzzle_menu, "&Copy as string", "Ctrl+Shift+C", self.copy_as_string
        )
        self._add_action(
            puzzle_menu, "&New empty board", QKeySequence.New, self.new_board
        )
        puzzle_menu.addSeparator()
        self._add_action(puzzle_menu, "&Quit", QKeySequence.Quit, self.close)

        solve_menu = self.menuBar().addMenu("&Solve")
        fill_action = self._add_action(
            solve_menu, "Fill in all &candidates", "Ctrl+Shift+F", self.fill_candidates
        )
        solve_action = self._add_action(
            solve_menu, "&Brute-force solve", "Ctrl+Shift+B", self.brute_force_solve
        )

        view_menu = self.menuBar().addMenu("&View")
        self._add_action(view_menu, "&Full screen", "F11", self.toggle_full_screen)

        # The same actions as buttons; menu and toolbar stay in sync automatically.
        toolbar = self.addToolBar("Solve")
        toolbar.setMovable(False)
        toolbar.addAction(fill_action)
        toolbar.addAction(solve_action)

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

    def fill_candidates(self) -> None:
        model_api.populate_candidates(self.board)
        self.board_widget.update()
        self.statusBar().showMessage("Filled in all candidates.", 3000)
        self.board_widget.setFocus()

    def brute_force_solve(self) -> None:
        if model_api.conflicts(self.board):
            self.statusBar().showMessage(
                "Fix the conflicting (red) digits first.", 5000
            )
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            solved = model_api.solve(self.board)
            multiple = solved is not None and model_api.has_multiple_solutions(
                self.board
            )
            # If the player's own digits block the solution, check the puzzle itself.
            puzzle_solvable = (
                solved is None
                and model_api.solve(model_api.givens_only(self.board)) is not None
            )
        finally:
            QApplication.restoreOverrideCursor()

        if solved is None:
            if puzzle_solvable:
                message = "No solution with your digits. At least one of them is wrong"
            else:
                message = "This puzzle has no solution."
            self.statusBar().showMessage(message, 5000)
            return

        self.board_widget.set_board(solved)
        if multiple:
            self.statusBar().showMessage(
                "Solved. None: this puzzle has more than one solution"
            )
        else:
            self.statusBar().showMessage("Solved!")
        self.board_widget.setFocus()

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
