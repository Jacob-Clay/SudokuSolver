import pytest

from sudoku.board import Board
from sudoku.gui import model_api

api = model_api


class TestNewBoard:
    def test_new_board_creates_empty_board(self):
        board: Board = api.new_board()
        assert isinstance(board, Board)
        assert board.is_solved() is False

    def test_new_board_returns_different_instances(self):
        board1: Board = api.new_board()
        board2: Board = api.new_board()
        assert board1 is not board2


class TestGridSize:
    def test_grid_size_standard_9x9(self):
        board = api.new_board()
        n_rows, n_cols = api.grid_size(board)
        assert n_rows == 9
        assert n_cols == 9

    def test_grid_size_returns_tuple(self):
        board = api.new_board()
        result = api.grid_size(board)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestGetCellValue:
    def test_get_empty_cell_returns_none(self):
        board = api.new_board()
        value = api.get_cell_value(board, (0, 0))
        assert value is None

    def test_get_cell_value_after_placing_digit(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        value = api.get_cell_value(board, (0, 0))
        assert value == 5

    def test_get_cell_value_different_coordinates(self):
        board = api.new_board()
        api.place(board, (4, 4), 9)
        assert api.get_cell_value(board, (4, 4)) == 9
        assert api.get_cell_value(board, (0, 0)) is None

    def test_get_cell_value_out_of_bounds_raises_error(self):
        board = api.new_board()
        with pytest.raises(IndexError):
            api.get_cell_value(board, (9, 9))


class TestGetCellCandidates:
    def test_get_candidates_empty_cell_returns_empty_set(self):
        board = api.new_board()
        candidates = api.get_cell_candidates(board, (0, 0))
        assert isinstance(candidates, frozenset)
        assert candidates == frozenset()

    def test_get_candidates_after_placing_digit(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        candidates = api.get_cell_candidates(board, (0, 0))
        # Cell with value should have empty candidates
        assert len(candidates) == 0

    def test_get_candidates_returns_frozenset(self):
        board = api.new_board()
        candidates = api.get_cell_candidates(board, (0, 0))
        assert isinstance(candidates, frozenset)


class TestIsCellGiven:
    def test_new_board_has_no_given_cells(self):
        board = api.new_board()
        for row in range(9):
            for col in range(9):
                assert api.is_cell_given(board, (row, col)) is False

    def test_placed_cell_is_not_given(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        assert api.is_cell_given(board, (0, 0)) is False

    def test_given_cell_from_string(self):
        # Create board with some given cells
        puzzle = "5" + "0" * 80
        board = api.board_from_string(puzzle)
        assert api.is_cell_given(board, (0, 0)) is True
        assert api.is_cell_given(board, (0, 1)) is False


class TestPlace:
    def test_place_digit_in_empty_cell(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        assert api.get_cell_value(board, (0, 0)) == 5

    def test_place_multiple_digits(self):
        board = api.new_board()
        api.place(board, (0, 0), 1)
        api.place(board, (1, 1), 2)
        api.place(board, (2, 2), 3)
        assert api.get_cell_value(board, (0, 0)) == 1
        assert api.get_cell_value(board, (1, 1)) == 2
        assert api.get_cell_value(board, (2, 2)) == 3

    def test_place_overwrites_previous_value(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        api.place(board, (0, 0), 9)
        assert api.get_cell_value(board, (0, 0)) == 9

    def test_place_invalid_digit_raises_error(self):
        board = api.new_board()
        with pytest.raises(ValueError):
            api.place(board, (0, 0), 10)

    def test_place_zero_raises_error(self):
        board = api.new_board()
        with pytest.raises(ValueError):
            api.place(board, (0, 0), 0)


class TestClear:
    def test_clear_placed_cell(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        api.clear(board, (0, 0))
        assert api.get_cell_value(board, (0, 0)) is None

    def test_clear_already_empty_cell(self):
        board = api.new_board()
        api.clear(board, (0, 0))
        assert api.get_cell_value(board, (0, 0)) is None

    def test_clear_given_cell_raises_error(self):
        puzzle = "5" + "0" * 80
        board = api.board_from_string(puzzle)
        with pytest.raises(ValueError):
            api.clear(board, (0, 0))


class TestToggleCandidate:
    def test_toggle_candidate_adds_to_empty_cell(self):
        board = api.new_board()
        api.toggle_candidate(board, (0, 0), 5)
        candidates = api.get_cell_candidates(board, (0, 0))
        assert 5 in candidates

    def test_toggle_candidate_removes_if_present(self):
        board = api.new_board()
        api.toggle_candidate(board, (0, 0), 5)
        api.toggle_candidate(board, (0, 0), 5)
        candidates = api.get_cell_candidates(board, (0, 0))
        assert 5 not in candidates

    def test_toggle_candidate_multiple_times(self):
        board = api.new_board()
        for digit in [1, 2, 3]:
            api.toggle_candidate(board, (0, 0), digit)
        candidates = api.get_cell_candidates(board, (0, 0))
        assert candidates == frozenset([1, 2, 3])
        for digit in [1, 2, 3]:
            api.toggle_candidate(board, (0, 0), digit)
        candidates = api.get_cell_candidates(board, (0, 0))
        assert candidates == frozenset()

    def test_toggle_candidate_invalid_digit_raises_error(self):
        board = api.new_board()
        with pytest.raises(ValueError):
            api.toggle_candidate(board, (0, 0), 10)


class TestConflicts:
    def test_new_board_has_no_conflicts(self):
        board = api.new_board()
        conflicts = api.conflicts(board)
        assert isinstance(conflicts, set)
        assert len(conflicts) == 0

    def test_conflicts_returns_set(self):
        board = api.new_board()
        result = api.conflicts(board)
        assert isinstance(result, set)

    def test_conflicts_with_duplicate_in_row(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        api.place(board, (0, 1), 5)
        conflicts = api.conflicts(board)
        assert (0, 0) in conflicts
        assert (0, 1) in conflicts


class TestIsSolved:
    def test_new_board_not_solved(self):
        board = api.new_board()
        assert api.is_solved(board) is False

    def test_returns_boolean(self):
        board = api.new_board()
        result = api.is_solved(board)
        assert isinstance(result, bool)


class TestRegionLookup:
    def test_region_lookup_returns_dict(self):
        board = api.new_board()
        lookup = api.region_lookup(board)
        assert isinstance(lookup, dict)

    def test_region_lookup_has_all_cells(self):
        board = api.new_board()
        lookup = api.region_lookup(board)
        assert len(lookup) == 81
        for row in range(9):
            for col in range(9):
                assert (row, col) in lookup

    def test_region_lookup_values_are_indices(self):
        board = api.new_board()
        lookup = api.region_lookup(board)
        indices = set(lookup.values())
        assert indices == set(range(9))  # 9 regions (3x3 boxes)

    def test_region_lookup_cells_in_same_region_have_same_index(self):
        board = api.new_board()
        lookup = api.region_lookup(board)
        # Cells in top-left 3x3 box should have the same region index
        box_indices = [lookup[(row, col)] for row in range(3) for col in range(3)]
        assert len(set(box_indices)) == 1

    def test_region_lookup_different_boxes_have_different_indices(self):
        board = api.new_board()
        lookup = api.region_lookup(board)
        top_left_index = lookup[(0, 0)]
        top_middle_index = lookup[(0, 3)]
        assert top_left_index != top_middle_index


class TestBoardFromString:
    def test_board_from_string_standard_81_chars(self):
        puzzle = "5" + "0" * 80
        board = api.board_from_string(puzzle)
        assert isinstance(board, Board)
        assert api.get_cell_value(board, (0, 0)) == 5

    def test_board_from_string_handles_spaces(self):
        puzzle = "5 0 0 0 0 0 0 0 0 " + "0" * 72
        board = api.board_from_string(puzzle)
        assert api.get_cell_value(board, (0, 0)) == 5

    def test_board_from_string_handles_newlines(self):
        puzzle = "5\n0\n0\n0\n0\n0\n0\n0\n0\n" + "0" * 72
        board = api.board_from_string(puzzle)
        assert api.get_cell_value(board, (0, 0)) == 5

    def test_board_from_string_handles_mixed_whitespace(self):
        puzzle = """
        5 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        0 0 0 0 0 0 0 0 0
        """
        board = api.board_from_string(puzzle)
        assert api.get_cell_value(board, (0, 0)) == 5

    def test_board_from_string_invalid_length_raises_error(self):
        puzzle = "5" * 80  # 80 chars instead of 81
        with pytest.raises(ValueError):
            api.board_from_string(puzzle)

    def test_board_from_string_invalid_character_raises_error(self):
        puzzle = "5A" + "0" * 79
        with pytest.raises(ValueError):
            api.board_from_string(puzzle)


class TestBoardToString:
    def test_board_to_string_empty_board(self):
        board = api.new_board()
        result = api.board_to_string(board)
        assert result == "0" * 81

    def test_board_to_string_with_placed_values(self):
        board = api.new_board()
        api.place(board, (0, 0), 5)
        api.place(board, (0, 1), 3)
        result = api.board_to_string(board)
        assert result[0] == "5"
        assert result[1] == "3"
        assert result[2:] == "0" * 79

    def test_board_to_string_round_trip(self):
        puzzle = "5" + "3" + "0" * 79
        board1 = api.board_from_string(puzzle)
        exported = api.board_to_string(board1)
        board2 = api.board_from_string(exported)
        assert api.board_to_string(board1) == api.board_to_string(board2)

    def test_board_to_string_returns_string(self):
        board = api.new_board()
        result = api.board_to_string(board)
        assert isinstance(result, str)
        assert len(result) == 81


EASY = (
    "300967001040302080020000070070000090000873000500010003004705100905000207800621004"
)
# Solved board with a 2x2 "deadly pattern" removed: exactly two solutions.
TWO_SOLUTIONS = (
    "295743861431865900876192543387459216612387495549216738763524189928671354154938600"
)


class TestPopulateCandidates:
    def test_populate_candidates_fill_empty_cells(self) -> None:
        board = api.board_from_string(EASY)
        api.populate_candidates(board)
        assert api.get_cell_candidates(board, (0, 1)) == board.get_possible_digits(0, 1)
        assert len(api.get_cell_candidates(board, (0, 1))) > 0

    def test_populate_candidates_leaves_filled_cells_empty(self) -> None:
        board = api.board_from_string(EASY)
        api.populate_candidates(board)
        assert api.get_cell_candidates(board, (0, 0)) == frozenset()

    def test_populate_candidates_replaces_player_candidates(self) -> None:
        board = api.board_from_string(EASY)
        api.toggle_candidate(board, (0, 1), 3)  # 3 is already in row 0
        api.populate_candidates(board)
        assert 3 not in api.get_cell_candidates(board, (0, 1))


class TestSolve:
    def test_solve_returns_new_solved_board(self) -> None:
        board = api.board_from_string(EASY)
        solved = api.solve(board)
        assert solved is not None
        assert solved is not board
        assert api.is_solved(solved)
        assert api.board_to_string(board) == EASY  # input unchanged

    def test_solve_keeps_givens(self) -> None:
        board = api.board_from_string(EASY)
        solved = api.solve(board)
        assert solved is not None
        assert api.is_cell_given(solved, (0, 0))
        assert api.get_cell_value(solved, (0, 0)) == 3

    def test_solve_returns_none_when_player_digit_is_wrong(self) -> None:
        board = api.board_from_string(EASY)
        solution = api.solve(board)
        assert solution is not None
        correct = api.get_cell_value(solution, (0, 1))
        assert correct is not None
        # a digit that causes no conflict but isn't the solution's digit
        wrong = next(d for d in sorted(board.get_possible_digits(0, 1)) if d != correct)
        api.place(board, (0, 1), wrong)
        assert api.conflicts(board) == set()
        assert api.solve(board) is None


class TestHasMultipleSolutions:
    def test_unique_puzzle(self) -> None:
        assert not api.has_multiple_solutions(api.board_from_string(EASY))

    def test_two_solutions(self) -> None:
        assert api.has_multiple_solutions(api.board_from_string(TWO_SOLUTIONS))

    def test_empty_board(self) -> None:
        assert api.has_multiple_solutions(api.new_board())


class TestGivensOnly:
    def test_givens_only_drops_player_digits(self) -> None:
        board = api.board_from_string(EASY)
        api.place(board, (0, 1), 5)
        result = api.givens_only(board)
        assert api.get_cell_value(result, (0, 1)) is None
        assert api.board_to_string(result) == EASY

    def test_givens_only_keeps_given_as_givens(self) -> None:
        result = api.givens_only(api.board_from_string(EASY))
        assert api.is_cell_given(result, (0, 0))

    def test_givens_only_shares_layout_and_leaves_input_alone(self) -> None:
        board = api.board_from_string(EASY)
        api.place(board, (0, 1), 5)
        result = api.givens_only(board)
        assert result.grid is board.grid
        assert api.get_cell_value(board, (0, 1)) == 5
