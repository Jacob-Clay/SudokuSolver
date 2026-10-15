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
    """Class representing a single cell in a sudoku grid.

    Attributes:
        value: The cell's value (1-9) if set, or None if empty.
        candidates: Set of possible values for this cell.
        given: Wheather this cell is a given (clue) that cannot be changed.
    """

    value: int | None = None
    candidates: set[int] = field(default_factory=set)
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

    Attributes:
        grid: The Grid object defining the board structure.
        cells: Dictionary mapping coordinates to Cell objects.
    """

    def __init__(
        self, regions: list[Unit] | None = None, grid: Grid | None = None
    ) -> None:
        """Initialize a sudoku board.

        Args:
            regions: List of Unit objects defining custom regions. If provided
            grid must be None.
            grid: A Grid object. If provided regions must be None. If neither is
            provided, creates a standard 9x9 sudoku board.

        Raises:
            ValueError: if both regions and grid are provided.
        """
        self.grid: Grid
        if regions:
            if grid:
                raise ValueError(
                    "Board can only be contructed with either a list of regions or a grid"
                )

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

            self.grid = Grid(n_rows=n_rows, n_cols=n_cols, regions=regions)
        elif grid:
            self.grid = grid
        else:
            self.grid = Grid(n_rows=9, n_cols=9, regions=self._create_standard_grid())

        self.cells: dict[Coordinate, Cell] = {}

        for row in range(9):
            for col in range(9):
                self.cells[(row, col)] = Cell()

    def _create_standard_grid(self) -> list[Unit]:
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

    def get_cell_value(self, row: int, col: int) -> int | None:
        """Get the value of a cell.

        Args:
            row: the row index (0-n_rows).
            col: the column index (0-n_cols).

        Returns:
            The cell's value (1-9) or None if empty.

        Raises:
            IndexError: if the coordinate is out of bounds.
        """
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

        return self.cells[(row, col)].value

    def set_cell_value(self, row: int, col: int, value: int) -> None:
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

        if self.cells[(row, col)].given:
            raise ValueError("Cell is given and therefore can't be changed")
        if value < 1 or value > 9:
            raise ValueError("Cell value must be 1-9")

        cell = self.cells[(row, col)]
        cell.value = value
        cell.candidates = set()

    def clear_cell(self, row: int, col: int) -> None:
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

        cell = self.cells[(row, col)]
        if cell.given:
            raise ValueError("Cell is given and therefore can't be changed")

        cell.value = None
        cell.candidates = set()

    def toggle_cell_candidate(self, row: int, col: int, value: int) -> None:
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

        cell = self.cells[(row, col)]
        if cell.given:
            raise ValueError("Cell is given and therefore can't be changed")
        if cell.is_solved():
            raise ValueError("Cell is solved and therefore can't have candidates")
        if value < 1 or value > 9:
            raise ValueError("Candidate value must be 1-9")

        if value in cell.candidates:
            cell.candidates.discard(value)
        else:
            cell.candidates.add(value)

    def set_given(self, row: int, col: int, value: int) -> None:
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

        if value < 1 or value > 9:
            raise ValueError("Cell value must be 1-9")

        cell = self.cells[(row, col)]
        cell.value = value
        cell.candidates = set()
        cell.given = True

    def is_complete(self) -> bool:
        for cell in self.cells.values():
            if not cell.is_solved():
                return False

        return True

    def get_conflicts(self) -> set[Coordinate]:
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
        return self.is_complete() and len(self.get_conflicts()) == 0

    def copy(self) -> Board:
        new_board = Board(grid=self.grid)
        new_cells: dict[Coordinate, Cell] = {}
        for coord, cell in self.cells.items():
            new_cells[coord] = Cell(cell.value, set(cell.candidates), cell.given)
        new_board.cells = new_cells

        return new_board

    @override
    def __str__(self) -> str:
        s = ""
        for i in range(self.grid.n_rows):
            for j in range(self.grid.n_cols):
                s += f"{self.cells[(i, j)]} "
            s += "\n"
        return s

    @classmethod
    def from_string(cls, input_str: str, regions: list[Unit] | None = None) -> Board:
        if len(input_str) != 81:
            raise ValueError("input string needs to be 81 char long")

        board: Board = cls(regions=regions)

        for index, char in enumerate(input_str):
            row = index // 9
            col = index % 9
            if char.isdigit():
                if char == "0":
                    continue
                board.set_given(row, col, int(char))
            elif char not in "*_.":
                raise ValueError("input string contains non valid character")

        return board
