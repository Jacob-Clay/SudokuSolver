from sudoku.grid import Coordinate, Grid, Unit, UnitType
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

    def add_candidate(self, num: int):
        """Add a candidate number to the cell."""
        self.candidates.add(num)

    def remove_candidate(self, num: int):
        """Remove a candidate number from the cell."""
        self.candidates.discard(num)

    def set_value(self, value: int | None):
        """Sets value field to value.

        Args:
            value: value of cell
        """
        self.value = value

    def is_solved(self) -> bool:
        """Check if the cell has a value assigned."""
        return self.value is not None

    def clear(self):
        """Reset the cell to empty state."""
        self.value = None
        self.candidates.clear()


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

    def get_cell_value(self, row: int, col: int):
        if row < 0 or row > 8:
            raise IndexError("Row must be 0-8")
        if col < 0 or col > 8:
            raise IndexError("Col must be 0-8")

        return self.cells[(row, col)].value
