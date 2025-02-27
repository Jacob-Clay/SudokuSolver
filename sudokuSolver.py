import sys

from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidgetAction, 
)

from input_output_dialogs import InputDialog, OutputDialog
from draw_widget import DrawWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TESTING!")
        self.setGeometry(100, 100, 550, 550)

        self.central_widget = DrawWidget(self)
        self.setCentralWidget(self.central_widget) 

        menu_bar = self.menuBar()

        input_given_action = QWidgetAction(self)
        input_given_action.setText("input givens")
        input_given_action.triggered.connect(self.input_given)
        menu_bar.addAction(input_given_action)

        output_action = QWidgetAction(self)
        output_action.setText("output board")
        output_action.triggered.connect(self.output_board)
        menu_bar.addAction(output_action)

        auto_clear_centermarks_action = QWidgetAction(self)
        auto_clear_centermarks_action.setText("auto clear centermarks")
        auto_clear_centermarks_action.triggered.connect(self.central_widget.auto_clear_centermarks)
        menu_bar.addAction(auto_clear_centermarks_action)

        add_all_centermarks_action = QWidgetAction(self)
        add_all_centermarks_action.setText("add all centermarks")
        add_all_centermarks_action.triggered.connect(self.central_widget.add_all_centermarks)
        menu_bar.addAction(add_all_centermarks_action)


    def input_given(self) -> None:
        dialog = InputDialog(self)
        dialog.exec()
    
    def recieve_data(self, data):
        self.central_widget.data = data
        self.central_widget.update()

    def output_board(self) -> None:
        dialog = OutputDialog(self, self.central_widget.data)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())