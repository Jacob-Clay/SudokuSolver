from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox
)

import re

class InputDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Input Dialog")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()

        self.label = QLabel("Enter in string representation of input:")
        layout.addWidget(self.label)

        self.text_input = QLineEdit(self)
        layout.addWidget(self.text_input)

        self.submit_button = QPushButton("Submit", self)
        layout.addWidget(self.submit_button)

        self.submit_button.clicked.connect(self.submit_text)

        self.setLayout(layout)

    def submit_text(self):
        input_text = self.text_input.text()
        if self.parent():
            if len(input_text) == 81 or len(input_text) == 162:
                self.make_cells(input_text)
                self.accept()
            else:
                QMessageBox.information(self, "Invalid Input", "Invalid input, input must be of length 81 or 162 imput was of length: " + str(len(input_text)))


    def make_cells(self, text):
        data = [[{} for _ in range(9)] for _ in range(9)]
        if len(text) == 81:
            for cell in range(len(text)):
                char = text[cell]
                if char == "0" or char == ".":
                    continue         
                i = cell % 9
                j = cell // 9
                data[i][j] = {"given": True, "value": char}

        else: # len(text) == 162
            string_split = re.findall('.{1,2}', text) # split string into 2 character strings
            for cell in range(len(string_split)): # iterate over each cell (2 character string)
                n = int(string_split[cell], 32) # convert 2 character string to int from base 32
                isClue = True if (n & 1) else False # check if the least significant bit is set to determine if the cell is a clue/given
                n = n >> 1 # shift n to the right by 1
                i = cell % 9 
                j = cell // 9 
                if bin(n).count('1') == 1: # check if number of bits set in n is 1
                    # save the number as a given
                    set_bits = self.get_set_bits(n)
                    if not isClue:
                        data[i][j] = {"given": True, "value": f"{set_bits[0]}"}
                    else:
                        data[i][j] = {"given": False, "value": f"{set_bits[0]}"}
                else:   
                    #save the number as a set of candidates
                    set_bits = self.get_set_bits(n)
                    data[i][j] = {"given": False, "centermarks": set_bits}
        self.parent().recieve_data(data)
    
    def get_set_bits(self, n):
        set_bits = []
        position = 1
        while n > 0: 
            if n & 1: # check if the least significant bit is set
                set_bits.append(position) 
            n >>= 1 # shift n to the right by 1
            position += 1 
        return set_bits   

    


class OutputDialog(QDialog):

    def __init__(self, parent=None, data={}) -> None:
        super().__init__(parent)

        self.setWindowTitle("Output Dialog")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()

        self.label = QLabel("Output:")
        layout.addWidget(self.label)

        self.make_cells_reverse(data)

        
    def make_cells_reverse(self, data):
        text = ""
        for i in range(9):  # Assuming a 9x9 Sudoku grid
            for j in range(9):
                cell = data[i][j]
                if "value" in cell:
                    value = int(cell["value"])
                    isClue = cell["given"]
                    n = (value << 1) | (1 if isClue else 0)  # Reconstruct integer from value and isClue
                    text += f"{n:02x}"  # Convert to 2-character hex string
                elif "centermarks" in cell:
                    set_bits = cell["centermarks"]
                    n = sum(1 << bit for bit in set_bits)  # Reconstruct integer from centermarks
                    text += f"{n:02x}"  # Convert to 2-character hex string
                else:
                    text += "00"
        print(text)
        # return text