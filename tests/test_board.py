import pytest

from sudoku.board import Board, Cell
from sudoku.grid import Coordinate, Unit, UnitType, Grid


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

    def test_board_creation(self) -> None:
        regions: tuple[Unit, ...] = (Unit(frozenset({(0, 0)}), 0, UnitType.REGION),)
        grid: Grid = Grid(1, 1, regions)

        with pytest.raises(ValueError):
            _ = Board(regions, grid)

        board: Board = Board(regions=regions)
        with pytest.raises(IndexError):
            board.set_cell_value(1, 0, 1)
            board.set_cell_value(0, 1, 1)
        assert len(board.cells) == 1
        assert board.grid.regions is regions

        board = Board(grid=grid)
        with pytest.raises(IndexError):
            board.set_cell_value(1, 0, 1)
            board.set_cell_value(0, 1, 1)
        assert len(board.cells) == 1
        assert board.grid is grid

    def test_cell_placement(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)

        assert board.get_cell_value(0, 0) == 1
        assert board.cells[(0, 0)].value == 1
        assert board.get_cell_value(1, 1) is None

    def test_clear_cell(self) -> None:
        board: Board = Board()

        board.set_cell_value(0, 0, 1)
        assert board.get_cell_value(0, 0) == 1
        board.clear_cell(0, 0)
        assert board.get_cell_value(0, 0) is None

        board.toggle_cell_candidate(0, 0, 1)
        assert board.get_cell_candidates(0, 0) == frozenset({1})
        board.clear_cell(0, 0)
        assert board.get_cell_candidates(0, 0) == frozenset()

    def test_is_cell_given(self) -> None:
        board: Board = Board()

        board.set_cell_value(0, 0, 1)
        assert not board.is_cell_given(0, 0)

        board.set_given(0, 0, 1)
        assert board.is_cell_given(0, 0)

        import_val = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"
        new_board: Board = Board.from_string(import_val)
        assert new_board.is_cell_given(0, 0)

    def test_toggle_cell_candidate(self) -> None:
        board: Board = Board()

        board.toggle_cell_candidate(0, 0, 1)
        assert 1 in board.get_cell_candidates(0, 0)
        board.toggle_cell_candidate(0, 0, 1)
        assert 1 not in board.get_cell_candidates(0, 0)

        board.set_cell_value(0, 0, 1)
        with pytest.raises(ValueError):
            board.toggle_cell_candidate(0, 0, 2)

    def test_cell_candidates_clear_upon_setting_value(self) -> None:
        board: Board = Board()

        board.toggle_cell_candidate(0, 0, 1)
        assert 1 in board.get_cell_candidates(0, 0)
        board.set_cell_value(0, 0, 3)
        assert board.get_cell_value(0, 0) == 3
        assert 1 not in board.get_cell_candidates(0, 0)

    def test_board_copy(self) -> None:
        board1: Board = Board()

        board1.toggle_cell_candidate(1, 1, 1)
        board1.set_cell_value(2, 2, 2)
        board1.set_given(3, 3, 3)

        board2: Board = board1.copy()
        assert board2.get_cell_value(1, 1) is None
        assert board2.get_cell_candidates(1, 1) == frozenset({1})
        assert board2.get_cell_value(2, 2) == 2
        assert board2.get_cell_value(3, 3) == 3
        assert not board2.is_cell_given(1, 1)
        assert not board2.is_cell_given(2, 2)
        assert board2.is_cell_given(3, 3)

        board1.toggle_cell_candidate(0, 0, 1)
        assert 1 in board1.get_cell_candidates(0, 0)
        assert 1 not in board2.get_cell_candidates(0, 0)

        board1.set_cell_value(0, 0, 1)
        assert board1.get_cell_value(0, 0) == 1
        assert board2.get_cell_value(0, 0) is None

        assert board1.grid is board2.grid

    def test_eq(self) -> None:
        import_val: str = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"
        board1: Board = Board.from_string(import_val)
        board2: Board = Board.from_string(import_val)

        assert board1 == board2

        board2 = Board.from_string(import_val.replace("5", "6"))
        assert board1 != board2

        assert board1 != import_val
        assert board1 != None
        assert board1 != 42
        assert board1 != {"some": "dict"}

    def test_to_string(self) -> None:
        import_val: str = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"
        board1: Board = Board.from_string(import_val)
        exported: str = board1.to_string()
        board2: Board = Board.from_string(exported)

        assert exported == import_val
        assert board1 == board2

    def test_str_format(self) -> None:
        import_val: str = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"
        board: Board = Board.from_string(import_val)
        board_str = str(board)

        lines = board_str.strip().split("\n")
        assert len(lines) == 9

        for line in lines:
            cells = line.split()
            assert len(cells) == 9

    def test_repr_format(self) -> None:
        import_val: str = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"
        board: Board = Board.from_string(import_val)
        board_repr = repr(board)

        assert board_repr.startswith("Board(")
        assert board_repr.endswith(")")
        assert import_val in board_repr

    def test_board_from_string(self) -> None:
        import_val: str = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"

        board: Board = Board.from_string(import_val)
        filled_coords: set[Coordinate] = {(0, 0), (4, 8), (6, 1), (7, 6), (8, 8)}

        assert len(board.cells) == 81
        assert len(board.grid.units) == 27
        for coord, cell in board.cells.items():
            assert cell.candidates == set()
            if coord in filled_coords:
                assert cell.value == 5
                assert cell.given
            else:
                assert cell.value is None
                assert not cell.given
        assert board.get_conflicts() == {(4, 8), (7, 6), (8, 8)}
        assert not board.is_complete()
        assert not board.is_solved()

        with pytest.raises(ValueError):
            _ = Board.from_string("12345")

        with pytest.raises(ValueError):
            _ = Board.from_string(
                "5x0000000000000000000000000000000000000000005000000000050000000000000500000000005"
            )

    @pytest.mark.parametrize("blank_char", ["*", "_", "."])
    def test_board_from_string_equivalents(self, blank_char):
        import_val: str = "500000000000000000000000000000000000000000005000000000050000000000000500000000005"

        reference: Board = Board.from_string(import_val)
        test_string: str = import_val.replace("0", blank_char)
        result: Board = Board.from_string(test_string)

        assert reference == result

    def test_board_from_string_custom_regions(self) -> None:
        coord_set: frozenset[Coordinate] = frozenset(
            {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)}
        )
        regions: tuple[Unit, ...] = (Unit(coord_set, 0, UnitType.REGION),)
        import_val: str = "100006"

        board: Board = Board.from_string(import_val, regions)
        assert len(board.grid.regions) == 1
        assert len(board.grid.columns) == 3
        assert len(board.grid.rows) == 2

        grid: Grid = board.grid
        for coord in board.cells:
            assert grid.get_peers_for_cell(*coord) == coord_set - {coord}
            assert len(grid.get_units_for_cell(*coord)) == 3
            assert regions[0] in grid.get_units_for_cell(*coord)

    def test_board_is_complete(self) -> None:
        import_val = "555555555555555555555555555555555555555555555555555555555555555555555555555555555"

        board: Board = Board.from_string(import_val)
        assert board.is_complete()
        assert not board.is_solved()

    def test_board_is_solved(self) -> None:
        import_val = "913568427687342915254197683479685132162734598538219764345926871726851349891473256"

        board: Board = Board.from_string(import_val)
        assert board.is_solved()

    def test_get_cell_candidates(self) -> None:
        board: Board = Board()

        assert len(board.get_cell_candidates(0, 0)) == 0

        board.toggle_cell_candidate(0, 0, 1)
        candidates: frozenset[int] = board.get_cell_candidates(0, 0)

        assert 1 in candidates
        with pytest.raises(AttributeError):
            candidates.add(2)

        assert 2 not in board.get_cell_candidates(0, 0)

    def test_remove_cell_candidate(self) -> None:
        board: Board = Board()

        board.toggle_cell_candidate(0, 0, 1)
        assert board.get_cell_candidates(0, 0) == frozenset({1})

        board.remove_cell_candidate(0, 0, 2)
        assert board.get_cell_candidates(0, 0) == frozenset({1})

        board.remove_cell_candidate(0, 0, 1)
        assert board.get_cell_candidates(0, 0) == frozenset()
        board.remove_cell_candidate(0, 0, 1)
        assert board.get_cell_candidates(0, 0) == frozenset()

        board.set_cell_value(0, 0, 1)
        board.remove_cell_candidate(0, 0, 2)  # This line implicitly tests no exception

        board.set_given(0, 0, 1)
        board.remove_cell_candidate(0, 0, 2)  # This line implicitly tests no exception


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

    def test_get_cell_candidates(self, row: int, col: int) -> None:
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
        board.set_cell_value(0, 7, 1)

        conflicts: set[Coordinate] = board.get_conflicts()
        assert (0, 0) in conflicts
        assert (0, 7) in conflicts
        assert len(conflicts) == 2

        board.clear_cell(0, 0)
        assert len(board.get_conflicts()) == 0

    def test_col_conflict(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)
        board.set_cell_value(7, 0, 1)

        conflicts: set[Coordinate] = board.get_conflicts()
        assert (0, 0) in conflicts
        assert (7, 0) in conflicts
        assert len(conflicts) == 2

        board.clear_cell(0, 0)
        assert len(board.get_conflicts()) == 0

    def test_non_conflict(self) -> None:
        board: Board = Board()
        board.set_cell_value(0, 0, 1)
        board.set_cell_value(3, 3, 1)

        assert len(board.get_conflicts()) == 0
