from sudoku.board import Board, Cell
import pytest


class TestCell:
    def test_cell_creation_default(self):
        cell: Cell = Cell()
        assert cell.value is None
        assert cell.candidates == set()
        assert not cell.given

    def test_cell_with_value(self):
        cell: Cell = Cell(value=5)
        assert cell.value == 5

    def test_cell_with_candidates(self):
        cell: Cell = Cell(candidates={1, 2, 3})
        assert 1 in cell.candidates
        assert len(cell.candidates) == 3

    def test_cell_as_given(self):
        cell: Cell = Cell(value=1, given=True)
        assert cell.value == 1
        assert cell.given


class TestBoard:
    def test_board_creation_default(self):
        board: Board = Board()
        assert len(board.cells) == 81
        assert len(board.grid.units) == 27
        for cell in board.cells.values():
            assert cell.value == None
            assert not cell.given
            assert cell.candidates == set()
        assert len(board.get_conflicts()) == 0
        assert not board.is_complete()
        assert not board.is_solved()

    def test_cell_placement(self):
        board: Board = Board()
        board.set_cell_value(0, 0, 1)

        assert board.get_cell_value(0, 0) == 1
        assert board.cells[(0, 0)].value == 1
        assert board.get_cell_value(1, 1) is None


@pytest.mark.parametrize(
    "row, col",
    [
        (-1, 0),
        (0, -1),
        (9, 0),
        (0, 9),
    ],
)
class TestBoardInvalidIndex:
    def test_get_cell_value(self, row, col):
        board: Board = Board()
        with pytest.raises(IndexError):
            board.get_cell_value(row, col)

    def test_clear_cell(self, row, col):
        board: Board = Board()
        with pytest.raises(IndexError):
            board.clear_cell(row, col)


@pytest.mark.parametrize(
    "row, col, val, expected_error",
    [
        (-1, 0, 10, IndexError),
        (0, -1, 10, IndexError),
        (9, 0, 10, IndexError),
        (0, 9, 10, IndexError),
        (0, 0, 0, ValueError),
        (0, 0, 10, ValueError),
    ],
)
class TestBoardInvalidValue:
    def test_set_cell_value(self, row, col, val, expected_error):
        board: Board = Board()
        with pytest.raises(expected_error):
            board.set_cell_value(row, col, val)

    def test_toggle_cell_candidate(self, row, col, val, expected_error):
        board: Board = Board()
        with pytest.raises(expected_error):
            board.toggle_cell_candidate(row, col, val)

    def test_set_given(self, row, col, val, expected_error):
        board: Board = Board()
        with pytest.raises(expected_error):
            board.set_given(row, col, val)
