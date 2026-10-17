"""Sudoku board representation and cell management.

This module provides the Board and Cell classes for manging a sudoku puzzle,
including cell values, candidates, and conflict detection.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import override

from sudoku.grid import Coordinate, Grid, Unit, UnitType


@dataclass
class Cell:
    """A single cell in a sudoku grid.

    A cell can be empty, have a single value, or have a set of candidate values.
    Given cells are immutable clues that cannot be changed.

    Attributes:
        value: The cell's value (1-9) if set, or None if unsolved.
        candidates: Set of possible values for this cell.
        given: Wheather this cell is a given (immutable clue).
    """

    value: int | None = None
    candidates: set[int] = field(default_factory=set[int])
    given: bool = False

    def is_solved(self) -> bool:
        """Check if the cell has a value assigned.

        Returns:
            True if the cell has a value, False otherwise
        """
        return self.value is not None

    @override
    def __str__(self) -> str:
        """Return string representation of the cell.

        Returns:
            The cell's value as a string, or '_' if empty.
        """
        if self.value:
            return f"{self.value}"
        else:
            return "_"


class Board:
    """A sudoku board containing cells organized into units and regions.

    The board manages a grid of cells and tracks their values and candidates. It
    can validate completeness, detect conflicts (duplicate values in units), and
    support both standard 9x9 Sudoku and custom grid sizes/shapes

    Attributes:
        grid: The Grid object defining the board structure (rows, columns, regions).
        cells: Dictionary mapping coordinates to Cell objects.
    """

    def __init__(
        self, regions: tuple[Unit, ...] | None = None, grid: Grid | None = None
    ) -> None:
        """Initialize a sudoku board.

        Exactly one of regions or grid must be provided. if neither is provided,
        creates a standard 9x9 Sudoku board with 3x3 regions.

        Args:
            regions: List of Unit objects defining custom regions. Automatically
            infers board dimensions from region coordinates. Mutually exclusive
            with grid.
            grid: A Grid object defining the board structure. Mutually exclusive
            with regions.

        Raises:
            ValueError: if both regions and grid are provided.
        """
        self.grid: Grid
        n_rows: int
        n_cols: int
        if regions:
            if grid:
                raise ValueError(
                    "Board can only be contructed with either a list of regions or a grid"
                )

            n_rows, n_cols = self._determine_dimensions(regions)

            self.grid = Grid(n_rows=n_rows, n_cols=n_cols, regions=tuple(regions))
        elif grid:
            self.grid = grid
            n_rows = grid.n_rows
            n_cols = grid.n_cols
        else:
            self.grid = Grid(
                n_rows=9, n_cols=9, regions=tuple(self._create_standard_grid())
            )
            n_rows = 9
            n_cols = 9

        self.cells: dict[Coordinate, Cell] = {}

        for row in range(n_rows):
            for col in range(n_cols):
                self.cells[(row, col)] = Cell()

    @staticmethod
    def _determine_dimensions(regions: tuple[Unit, ...]) -> tuple[int, int]:
        """Determine grid dimensions from regions.

        Args:
            regions: List of Unit objects.

        Returns:
            Tuple of (n_rows, n_cols).
        """
        n_rows: int = 0
        n_cols: int = 0
        combined_sets_of_coords: set[Coordinate] = set()
        for region in regions:
            combined_sets_of_coords.update(region.coords)
        for row, col in combined_sets_of_coords:
            n_rows = max(n_rows, row)
            n_cols = max(n_cols, col)

        n_rows += 1  # coords is 0 indexed
        n_cols += 1  # coords is 0 indexed

        return (n_rows, n_cols)

    def _create_standard_grid(self) -> list[Unit]:
        """Create the 9 regions for a standard 9x9 Sudoku.

        Returns:
            A list of 9 Unit objects representing the 3x3 boxes of standard Sudoku.
        """
        regions: list[Unit] = []
        region_id = 0

        for box_row in range(3):
            for box_col in range(3):
                cells_in_region: set[Coordinate] = set()
                for row in range(box_row * 3, box_row * 3 + 3):
                    for col in range(box_col * 3, box_col * 3 + 3):
                        cells_in_region.add((row, col))
                regions.append(
                    Unit(frozenset(cells_in_region), region_id, UnitType.REGION)
                )
                region_id += 1

        return regions

    def _is_valid_coordinate(self, row: int, col: int) -> bool:
        """Check if coordinates are within the board bounds.

        Args:
            row: The row index.
            col: the column index.

        Returns:
            True if coordinates are valid, False otherwise.
        """
        return (
            row >= 0 and row < self.grid.n_rows and col >= 0 and col < self.grid.n_cols
        )

    def _check_coordinate(self, row: int, col: int) -> None:
        """Check if coordinates are within the board bounds.

        Args:
            row: The row index.
            col: The column index.

        Raises:
            IndexError: If the coordinate is out of board bounds.
        """
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

    def _is_valid_digit(self, val: int) -> bool:
        """Check if value is valid (1-9).

        Args:
            val: The value to check.

        Returns:
            True if value is 1-9, False otherwise.
        """
        return val >= 1 and val <= 9

    def _check_digit(self, val: int) -> None:
        """Check if value is valid (1-9).

        Args:
            val: The value to check.

        Raises:
            ValueError: If the value is not in the range 1-9.
        """
        if not self._is_valid_digit(val):
            raise ValueError("value must be 1-9")

    def get_cell_value(self, row: int, col: int) -> int | None:
        """Get the value of a cell.

        Args:
            row: The row index (0 to n_rows-1).
            col: The column index (0 to n_cols-1).

        Returns:
            The cell's value (1-9) or None if empty.

        Raises:
            IndexError: If the coordinate is out of bounds.
        """
        self._check_coordinate(row, col)

        return self.cells[(row, col)].value

    def is_cell_given(self, row: int, col: int) -> bool:
        """Checks if a cell is given (immutable clue).

        Args:
            row: The row index (0 to n_rows-1).
            col: The column index (0 to n_cols-1).

        Returns:
            True if the cell is given, false otherwise.

        Raises:
            IndexError: If the coordinate is out of bounds.
        """
        self._check_coordinate(row, col)

        return self.cells[(row, col)].given

    def set_cell_value(self, row: int, col: int, value: int) -> None:
        """Set the value of a cell to a single digit, clearing candidates.

        Args:
            row: The row index (0 to n_rows-1).
            col: The column index (0 to n_cols-1).
            value: The value to set (1-9)

        Raises:
            IndexError: If the coordinate is out of bounds.
            ValueError: If the cell is a given (immutable) or value is not 1-9.
        """
        self._check_coordinate(row, col)
        self._check_digit(value)

        cell: Cell = self.cells[(row, col)]
        if cell.given:
            raise ValueError("Cell is given and therefore can't be changed")

        cell.value = value
        cell.candidates = set()

    def clear_cell(self, row: int, col: int) -> None:
        """Clear a cell's value and candidates.

        Args:
            row: The row index (0 to n_rows-1).
            col: The column index (0 to n_cols-1).

        Raises:
            IndexError: If the coordinate is out of bounds.
            ValueError: If the cell is a given (immutable).
        """
        self._check_coordinate(row, col)

        cell = self.cells[(row, col)]
        if cell.given:
            raise ValueError("Cell is given and therefore can't be changed")

        cell.value = None
        cell.candidates = set()

    def toggle_cell_candidate(self, row: int, col: int, value: int) -> None:
        """Add or remove a candidate from a cell.

        If the value is already a candidate, it is removed. Otherwise, it is added.

        Args:
            row: The row index (0 to n_rows-1).
            col: The column index (0 to n_cols-1).
            value: The candidate value to toggle (1-9).

        Raises:
            IndexError: If the coordinate is out of bounds.
            ValueError: If the cell is a given, already solved, or value is not 1-9.
        """
        self._check_coordinate(row, col)
        self._check_digit(value)

        cell: Cell = self.cells[(row, col)]
        if cell.given:
            raise ValueError("Cell is given and therefore can't be changed")
        if cell.is_solved():
            raise ValueError("Cell is solved and therefore can't have candidates")

        if value in cell.candidates:
            cell.candidates.discard(value)
        else:
            cell.candidates.add(value)

    def get_cell_candidates(self, row: int, col: int) -> frozenset[int]:
        """Retrieve all candidate vales for a cell.

        Returns an immutable set of all possible values that can be placed in
        the specified cell, based on current board state.

        Args:
            row: The row index (0 to n_rows-1).
            col: The column index (0 to n_cols-1).

        Returns:
            A frozenset containing all candidate values for the cell.

        Raises:
            IndexError: If the coordinate is out of bounds.
        """
        self._check_coordinate(row, col)

        cell: Cell = self.cells[(row, col)]
        return frozenset(cell.candidates)

    def remove_cell_candidate(self, row: int, col: int, value: int) -> None:
        """Remove a candidate value from a cell.

        Eliminates the specified value from the cell's set of possible candidates.
        Has no effect if the value is not currently a candidate.

        Args:
            row: The row index (0 to n_rows-1).
            col: the column index (0 to n_cols-1).
            value: the candidate value to remove (1-9).

        Raises:
            IndexError: If the coordinate is out of bounds.
            ValueError: if value is not 1-9
        """
        self._check_coordinate(row, col)
        self._check_digit(value)

        cell: Cell = self.cells[(row, col)]
        cell.candidates.discard(value)

    def get_possible_digits(self, row: int, col: int) -> frozenset[int]:
        """Return the set of valid digit values for a cell.

        Determines which numbers (1-9) can be placed in the specified cell by
        excluding values that already appear in the cell's peers (cells that
        share a row, column or region).

        Args:
            row: The row index of the cell.
            col: The column index of the cell.

        Returns:
            A set of integers (1-9) representing valid digits for the cell.
            An empty set if all values are already taken by peers or cell is
            already set.
        """
        if self.get_cell_value(row, col) is not None:
            return frozenset()

        possible_candidates: set[int] = {1, 2, 3, 4, 5, 6, 7, 8, 9}

        for peer_coord in self.grid.get_peers_for_cell(row, col):
            cell_value: int | None = self.get_cell_value(*peer_coord)
            if cell_value is not None:
                possible_candidates.discard(cell_value)

        return frozenset(possible_candidates)

    def populate_candidates(self) -> None:
        """Populate candidate sets for all cells based on current board state.

        Iterates through every cell in the grid and computes the set of valid
        values (1-9) that could legally occupy that cell, given sudoku
        constraints.

        Side Effects:
            Overwrites the `candidates` attribute (a set) of every cell in `self.cells`.
            Cells are mutated in place; no return value.
        """
        for coord, cell in self.cells.items():
            cell.candidates = set(self.get_possible_digits(*coord))

    def set_given(self, row: int, col: int, value: int) -> None:
        """Set a cell as a given (immutable clue) with a value.

        Given cells cannot be modified or cleared.

        Args:
            row: The row index (0 to n_rows-1).
            col: The column index (0 to n_cols-1).
            value: The value to set (1-9).

        Raises:
            IndexError: If the coordinate is out of bounds.
            ValueError: If value is not 1-9.
        """
        self._check_coordinate(row, col)
        self._check_digit(value)

        cell: Cell = self.cells[(row, col)]
        cell.value = value
        cell.candidates = set()
        cell.given = True

    def is_complete(self) -> bool:
        """Check if all cells have assigned values.

        Returns:
            True if every cell has a value, False otherwise.
        """
        for cell in self.cells.values():
            if not cell.is_solved():
                return False

        return True

    def get_conflicts(self) -> set[Coordinate]:
        """Find all cells that violate Sudoku constraints.

        A conflict occurs when two or more cells in the same unit (row, column,
        or region) have the same value.

        Returns:
            A set of cell coordinates that contain conflicting values.
        """
        conflicts: set[Coordinate] = set()
        for unit in self.grid.units:
            value_to_coords: dict[int, set[Coordinate]] = defaultdict(set)
            for coord in unit.coords:
                value = self.cells[coord].value
                if value is None:
                    continue
                value_to_coords[value].add(coord)

            for value, coords in value_to_coords.items():
                if len(coords) <= 1:
                    continue
                conflicts.update(coords)

        return conflicts

    def is_solved(self) -> bool:
        """Check if the board is completely and validly solved.

        Returns:
            True if all cells are filled and no conflicts exist, False otherwise.
        """
        return self.is_complete() and len(self.get_conflicts()) == 0

    def copy(self) -> Board:
        """Create a deep copy of the board.

        Returns:
            A new Board instance with the same grid and cell states as this board.
        """
        new_board: Board = Board(grid=self.grid)
        new_cells: dict[Coordinate, Cell] = {}
        for coord, cell in self.cells.items():
            new_cells[coord] = Cell(cell.value, set(cell.candidates), cell.given)
        new_board.cells = new_cells

        return new_board

    @override
    def __str__(self) -> str:
        """Return a string representation of the board.

        Returns:
            A multi-line string showing the board grid with cell values.
        """
        s = ""
        for i in range(self.grid.n_rows):
            for j in range(self.grid.n_cols):
                s += f"{self.cells[(i, j)]} "
            s += "\n"
        return s

    @override
    def __repr__(self) -> str:
        return f"Board({self.to_string()})"

    @override
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Board):
            return NotImplemented
        return self.grid == value.grid and self.cells == value.cells

    def to_string(self) -> str:
        """Export the current board state as a string.

        Creates a string representation of the board in row-major order,
        with digits 1-9 for given/solved values and '0' for empty cells.
        Does not preserve information about which cells are given vs. solved,
        or candidate values. Use from_string() to reimport.

        Returns:
            A string of n_rows * n_cols characters representing the board.
        """
        s = ""
        for cell in self.cells.values():
            if cell.value:
                s += f"{cell.value}"
            else:
                s += "0"

        return s

    @classmethod
    def from_string(
        cls, input_str: str, regions: tuple[Unit, ...] | None = None
    ) -> Board:
        """Create a board from a string representation.

        The input string must be exactly n_rows * n_cols characters long,
        representing the board in row-major order (left-to-right,
        top-to-bottom). Digits 1-9 are given values, while '0', '*', '_', and
        '.' represent empty cells.

        Args:
            input_str: A string of n_rows * n_cols characters representing the
            board state.
            regions: Optional list of Unit objects for a custom board. If not
            provided, creates a standard 9x9 Sudoku board.

        Returns:
            A new Board instance with cells initialized from the input string.

        Raises:
            ValueError: If input_str is not exactly n_rows * n_cols characters
            or contains invalid characters.
        """
        n_rows: int
        n_cols: int
        if regions:
            n_rows, n_cols = cls._determine_dimensions(regions)
        else:
            n_rows = 9
            n_cols = 9

        if len(input_str) != n_rows * n_cols:
            raise ValueError("input string needs to be n_rows * n_cols char long")

        board: Board = cls(regions=regions)

        for index, char in enumerate(input_str):
            row = index // n_cols
            col = index % n_cols
            if char.isdigit():
                if char == "0":
                    continue
                board.set_given(row, col, int(char))
            elif char not in "*_.":
                raise ValueError("input string contains non valid character")

        return board
