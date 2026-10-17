import pytest

from sudoku.board import Board
from sudoku.solvers import brute_force


class TestBruteForce:
    def test_board_with_conflict(self):
        input_str: str = "1" * 81
        board: Board = Board.from_string(input_str)
        assert brute_force.solve(board) is None
        assert brute_force.count_solutions(board) == 0

    def test_easy_puzzle(self):
        board: Board = Board.from_string(
            "300967001040302080020000070070000090000873000500010003004705100905000207800621004"
        )
        solved_board: Board | None = brute_force.solve(board)

        assert solved_board is not None
        assert board == Board.from_string(
            "300967001040302080020000070070000090000873000500010003004705100905000207800621004"
        )
        assert solved_board.is_solved()

        assert brute_force.count_solutions(board) == 1

    def test_already_solved_board(self):
        board: Board = Board.from_string(
            "649157832821396745375284196437928561518763429296415378153672984964831257782549613"
        )
        solved_board: Board | None = brute_force.solve(board)

        assert board.is_solved()
        assert solved_board is not None
        assert solved_board == board

        assert brute_force.count_solutions(board) == 1

    @pytest.mark.timeout(3)
    def test_hard_puzzle(self):
        board: Board = Board.from_string(
            "800000000003600000070090200050007000000045700000100030001000068008500010090000400"
        )
        solved_board: Board | None = brute_force.solve(board)
        assert solved_board is not None

    def test_finds_a_nonunique_solution(self):
        board: Board = Board()
        solved_board: Board | None = brute_force.solve(board)

        assert solved_board is not None
        assert brute_force.count_solutions(board) == 2
        assert brute_force.count_solutions(board, 1) == 1

    def test_count_solutions(self):
        board: Board = Board()

        with pytest.raises(ValueError):
            _ = brute_force.count_solutions(board, limit=0)

        with pytest.raises(ValueError):
            _ = brute_force.count_solutions(board, limit=-1)

        board = Board.from_string(
            "295743861431865900876192543387459216612387495549216738763524189928671354154938600"
        )
        assert brute_force.count_solutions(board) == 2
        assert brute_force.count_solutions(board, 100) == 2
