"""A brute force solver for Sudoku boards."""

from collections.abc import Generator

from sudoku.board import Board
from sudoku.grid import Coordinate


def solve(board: Board) -> Board | None:
    """Uses brute force techniques to solve a Sudoku board.

    Args:
        board: The board to solve.

    Returns:
        A new solved Sudoku board if one exists or None if no solution exists.
    """
    return next(_search(board), None)


def _search(board: Board) -> Generator[Board]:
    coord_fewest_digits: Coordinate = _get_cell_with_fewest_possible_digits(board)
    possible_digits: frozenset[int] = board.get_possible_digits(*coord_fewest_digits)

    if board.is_solved():
        yield board
        return
    if board.get_conflicts() != set():
        return

    for digit in possible_digits:
        new_board: Board = board.copy()
        new_board.set_cell_value(*coord_fewest_digits, digit)
        yield from _search(new_board)


def _get_cell_with_fewest_possible_digits(board: Board) -> Coordinate:
    n_digits: int = 1000  # way bigger than any board should ever be
    cell_with_fewest_possible_digits: Coordinate = (0, 0)
    for row in range(board.grid.n_rows):
        for col in range(board.grid.n_cols):
            if board.get_cell_value(row, col) is not None:
                continue
            t_n_digits: int = len(board.get_possible_digits(row, col))
            if t_n_digits < n_digits:
                n_digits = t_n_digits
                cell_with_fewest_possible_digits = (row, col)
            if n_digits == 1:
                return cell_with_fewest_possible_digits

    return cell_with_fewest_possible_digits


def count_solutions(board: Board, limit: int = 2) -> int:
    """Counts how many possible solutions a board has up to limit.

    Args:
        board: The sudoku board to count solutions of.
        limit: The maximum number of solutions it should count to for testing
        non-uniqueness use 2.

    Returns:
        Number of possible solutions up to limit (0-limit).

    Raises:
        ValueError: When limit is less than 1.
    """
    if limit <= 0:
        raise ValueError("Limit msut be at least 1")

    n_solutions: int = 0
    for _ in _search(board):
        n_solutions += 1
        if n_solutions == limit:
            return n_solutions
    return n_solutions
