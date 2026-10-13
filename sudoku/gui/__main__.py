"""Start the app with:  python -m sudoku.gui"""

import sys

from PySide6.QtWidgets import QApplication

from sudoku.gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
