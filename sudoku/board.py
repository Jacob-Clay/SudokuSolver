from sudoku.grid import Coordinate, Grid, Unit, UnitType
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Cell:
    """Class representing a single cell in a sudoku grid.

    Attributes:
        value: Value of cell if set, typically 1-9
        candidates: Set of possible values
    """

    value: int | None = None
    candidates: set[int] = field(default_factory=set)
    given: bool = False

    def is_solved(self) -> bool:
        """Check if the cell has a value assigned."""
        return self.value is not None

    def __str__(self) -> str:
        if self.value:
            return f"{self.value}"
        else:
            return "_"


class Board:
    def __init__(self, regions: list[Unit] | None = None) -> None:
        if regions:
            self.grid = Grid(n_rows=9, n_cols=9, regions=regions)
        else:
            self.grid = Grid(n_rows=9, n_cols=9, regions=self.create_standard_grid())

        self.cells: dict[Coordinate, Cell] = {}

        for row in range(9):
            for col in range(9):
                self.cells[(row, col)] = Cell()

    def create_standard_grid(self) -> list[Unit]:
        regions = []
        region_id = 0

        for box_row in range(3):
            for box_col in range(3):
                cells_in_region = set()
                for row in range(box_row * 3, box_row * 3 + 3):
                    for col in range(box_col * 3, box_col * 3 + 3):
                        cells_in_region.add((row, col))
                regions.append(Unit(cells_in_region, region_id, UnitType.REGION))
                region_id += 1

        return regions

    def _is_valid_coordinate(self, row: int, col: int) -> bool:
        return row >= 0 and row <= 8 and col >= 0 and col <= 8

    def get_cell_value(self, row: int, col: int):
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

    def add_cell_candidate(self, row: int, col: int, value: int) -> None:
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

        cell = self.cells[(row, col)]
        if cell.given:
            raise ValueError("Cell is given and therefore can't be changed")
        if cell.is_solved():
            raise ValueError("Cell is solved and therefore can't have candidates")

        cell.candidates.add(value)

    def set_given(self, row: int, col: int, value: int) -> None:
        if not self._is_valid_coordinate(row, col):
            raise IndexError("Invalid cell coordinate")

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
            value_to_cords: dict[int, set[Coordinate]] = defaultdict(set)
            for coord in unit.cords:
                value = self.cells[coord].value
                if value is None:
                    continue
                value_to_cords[value].add(coord)

            for value, cords in value_to_cords.items():
                if len(cords) <= 1:
                    continue
                conflicts.update(cords)

        return conflicts

    def is_solved(self) -> bool:
        return self.is_complete() and len(self.get_conflicts()) == 0

    def __str__(self) -> str:
        s = ""
        for i in range(self.grid.n_rows):
            for j in range(self.grid.n_cols):
                s += f"{self.cells[(i, j)]} "
            s += "\n"
        return s
