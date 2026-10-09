from sudoku.board import Cell


class TestCell:
    def test_cell_creation_default(self):
        cell = Cell()
        assert cell.value == None
        assert cell.candidates == set()
        assert cell.given == False

    def test_cell_with_value(self):
        cell = Cell(value=5)
        assert cell.value == 5

    def test_cell_with_candidates(self):
        cell = Cell(candidates={1, 2, 3})
        assert 1 in cell.candidates
        assert len(cell.candidates) == 3
