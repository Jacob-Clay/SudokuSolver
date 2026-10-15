from sudoku.board import Board, Cell
import pytest

from sudoku.grid import Coordinate


class TestCell:
    def test_cell_creation_default(self) -> None:
        cell: Cell = Cell()
        assert cell.value is None
        assert cell.candidates == set()
        assert not cell.given

    def test_cell_with_value(self) -> None:
        cell: Cell = Cell(value=5)
        assert cell.value == 5

    def test_cell_with_candidates(self) -> None:
        cell: Cell = Cell(candidates={1, 2, 3})
        assert 1 in cell.candidates
        assert len(cell.candidates) == 3

    def test_cell_as_given(self) -> None:
        cell: Cell = Cell(value=1, given=True)
        assert cell.value == 1
        assert cell.given


class TestBoard:
    def test_board_creation_default(self) -> None:
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

    def test_cell_placement(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)

        assert board.get_cell_value(0, 0) == 1
        assert board.cells[(0, 0)].value == 1
        assert board.get_cell_value(1, 1) is None

    def test_toggle_cell_candidate(self) -> None:
        board: Board = Board()

        board.toggle_cell_candidate(0, 0, 1)
        assert 1 in board.get_cell_candidates(0, 0)
        board.toggle_cell_candidate(0, 0, 1)
        assert 1 not in board.get_cell_candidates(0, 0)

    def test_cell_candidates_clear_upon_setting_value(self) -> None:
        board: Board = Board()

        board.toggle_cell_candidate(0, 0, 1)
        assert 1 in board.get_cell_candidates(0, 0)
        board.set_cell_value(0, 0, 3)
        assert board.get_cell_value(0, 0) == 3
        assert 1 not in board.get_cell_candidates(0, 0)

    def test_board_copy(self) -> None:
        board1: Board = Board()
        board2: Board = board1.copy()

        board1.toggle_cell_candidate(0, 0, 1)
        assert 1 in board1.get_cell_candidates(0, 0)
        assert 1 not in board2.get_cell_candidates(0, 0)

        board1.set_cell_value(0, 0, 1)
        assert board1.get_cell_value(0, 0) == 1
        assert board2.get_cell_value(0, 0) is None

        assert board1.grid is board2.grid

    def test_board_input(self) -> None:
        import_val = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"

        board: Board = Board.from_string(import_val)
        assert board.get_cell_value(0, 0) == 5
        assert board.get_cell_value(0, 1) is None
        assert board.get_cell_value(4, 8) == 5
        assert board.get_cell_value(6, 1) == 5
        assert board.get_cell_value(7, 6) == 5
        assert board.get_cell_value(8, 8) == 5

    def test_board_is_complete(self) -> None:
        import_val = "555555555555555555555555555555555555555555555555555555555555555555555555555555555"

        board: Board = Board.from_string(import_val)
        assert board.is_complete()
        assert not board.is_solved()

    def test_board_is_solved(self) -> None:
        import_val = "913568427687342915254197683479685132162734598538219764345926871726851349891473256"

        board: Board = Board.from_string(import_val)
        assert board.is_solved()


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
    def test_get_cell_value(self, row: int, col: int) -> None:
        board: Board = Board()
        with pytest.raises(IndexError):
            _ = board.get_cell_value(row, col)

    def test_clear_cell(self, row: int, col: int) -> None:
        board: Board = Board()
        with pytest.raises(IndexError):
            board.clear_cell(row, col)

    def test_get_cell_candadiates(self, row: int, col: int) -> None:
        board: Board = Board()
        with pytest.raises(IndexError):
            _ = board.get_cell_candidates(row, col)


type BoardError = ValueError | IndexError


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
    def test_set_cell_value(
        self, row: int, col: int, val: int, expected_error: type[BoardError]
    ) -> None:
        board: Board = Board()
        with pytest.raises(expected_error):
            board.set_cell_value(row, col, val)

    def test_toggle_cell_candidate(
        self, row: int, col: int, val: int, expected_error: type[BoardError]
    ) -> None:
        board: Board = Board()
        with pytest.raises(expected_error):
            board.toggle_cell_candidate(row, col, val)

    def test_set_given(
        self, row: int, col: int, val: int, expected_error: type[BoardError]
    ) -> None:
        board: Board = Board()
        with pytest.raises(expected_error):
            board.set_given(row, col, val)

    def test_remove_cell_candidate(
        self, row: int, col: int, val: int, expected_error: type[BoardError]
    ) -> None:
        board: Board = Board()
        with pytest.raises(expected_error):
            board.remove_cell_candidate(row, col, val)


@pytest.fixture
def given_setup() -> Board:
    board: Board = Board()
    board.set_given(0, 0, 1)

    return board


class TestBoardPlaceOverGiven:
    def test_set_cell_value_over_given(self, given_setup: Board) -> None:
        board: Board = given_setup
        with pytest.raises(ValueError):
            board.set_cell_value(0, 0, 1)

    def test_clear_cell_over_given(self, given_setup: Board) -> None:
        board: Board = given_setup
        with pytest.raises(ValueError):
            board.clear_cell(0, 0)

    def test_toggle_cell_candidate_over_given(self, given_setup: Board) -> None:
        board: Board = given_setup
        with pytest.raises(ValueError):
            board.toggle_cell_candidate(0, 0, 1)


class TestBoardConflicts:
    def test_region_conflict(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)
        board.set_cell_value(2, 2, 1)

        conflicts: set[Coordinate] = board.get_conflicts()
        assert (0, 0) in conflicts
        assert (2, 2) in conflicts
        assert len(conflicts) == 2

        board.clear_cell(0, 0)
        assert len(board.get_conflicts()) == 0

    def test_row_conflict(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)
        board.set_cell_value(7, 0, 1)

        conflicts: set[Coordinate] = board.get_conflicts()
        assert (0, 0) in conflicts
        assert (7, 0) in conflicts
        assert len(conflicts) == 2

        board.clear_cell(0, 0)
        assert len(board.get_conflicts()) == 0

    def test_col_conflict(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)
        board.set_cell_value(0, 7, 1)

        conflicts: set[Coordinate] = board.get_conflicts()
        assert (0, 0) in conflicts
        assert (0, 7) in conflicts
        assert len(conflicts) == 2

        board.clear_cell(0, 0)
        assert len(board.get_conflicts()) == 0

    def test_non_conflict(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)
        board.set_cell_value(3, 3, 1)

        assert len(board.get_conflicts()) == 0
