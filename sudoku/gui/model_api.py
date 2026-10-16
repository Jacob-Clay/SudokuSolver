"""The only place the GUI touches the model.

Every call from the GUI into Board / Grid goes through these functions. The GUI
passes cells around as (row, col) tuples; this file unpacks them for the board.
If you rename something in board.py or grid.py, update it here and nothing else.

Uses from the model:
    Board()
    board.grid.n_rows, board.grid.n_cols, board.grid.regions (units with .coords)
    board.get_cell_value / get_cell_condidates / is_cell_given
    board.cells[(row, col)]  -> Cell with .value, .candidates, .given
    board.set_cell_value / clear_cell / toggle_cell_candidate  (raise ValueError)
    board.get_conflicts(), board.is_solved(), board.from_string()
"""

from sudoku.board import Board, Cell

type Coordinate = tuple[int, int]


def new_board() -> Board:
    return Board()


def grid_size(board: Board) -> tuple[int, int]:
    return board.grid.n_rows, board.grid.n_cols


def get_cell_candidates(board: Board, coord: Coordinate) -> frozenset[int]:
    return board.get_cell_candidates(*coord)


def get_cell_value(board: Board, coord: Coordinate) -> int | None:
    return board.get_cell_value(*coord)


def is_cell_given(board: Board, coord: Coordinate) -> bool:
    return board.is_cell_given(*coord)


def place(board: Board, coord: Coordinate, digit: int) -> None:
    board.set_cell_value(*coord, digit)


def clear(board: Board, coord: Coordinate) -> None:
    board.clear_cell(*coord)


def toggle_candidate(board: Board, coord: Coordinate, digit: int) -> None:
    board.toggle_cell_candidate(*coord, digit)


def conflicts(board: Board) -> set[Coordinate]:
    return board.get_conflicts()


def is_solved(board: Board) -> bool:
    return board.is_solved()


def region_lookup(board: Board) -> dict[Coordinate, int]:
    """Map each cell to the index of its region (used to draw thick borders)."""
    lookup: dict[Coordinate, int] = {}
    for index, region in enumerate(board.grid.regions):
        for coord in region.coords:
            lookup[coord] = index
    return lookup


def board_from_string(text: str) -> Board:
    """New board from an 81-character string. Raises ValueError on bad input."""
    text = "".join(text.split())  # tolerate spaces and line breaks when pasting
    return Board.from_string(text)


def board_to_string(board: Board) -> str:
    """Values only, '0' for empty."""
    return board.to_string()
