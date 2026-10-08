"""All needed dataclasses for a grid of cells including their regions."""

from dataclasses import dataclass, field
from enum import Enum

type Coordinate = tuple[int, int]


class UnitType(Enum):
    ROW = "row"
    COLUMN = "column"
    REGION = "region"


@dataclass
class Unit:
    cell_cords: set[Coordinate]
    unit_id: int
    unit_type: UnitType

    def contains(self, row: int, col: int) -> bool:
        """Check if this unit contains a cell.

        Args:
            row: the row of the cell to check
            col: the column of the cell to check

        Returns:
            True if in region, else False
        """
        return (row, col) in self.cell_cords


@dataclass
class Grid:
    n_rows: int
    n_cols: int
    regions: list[Unit]
    columns: list[Unit] = field(init=False, default_factory=list)
    rows: list[Unit] = field(init=False, default_factory=list)
    units: list[Unit] = field(init=False, default_factory=list)
    cell_to_peers: dict[Coordinate, set[Coordinate]] = field(
        init=False, default_factory=dict
    )
    cell_to_units: dict[Coordinate, list[Unit]] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self):
        unit_id = 1
        for col in range(self.n_cols):
            cells = {(row, col) for row in range(self.n_rows)}
            new_unit = Unit(cells, unit_id, UnitType.COLUMN)
            self.columns.append(new_unit)
            self.units.append(new_unit)
            unit_id += 1

        unit_id = 1
        for row in range(self.n_rows):
            cells = {(row, col) for col in range(self.n_cols)}
            new_unit = Unit(cells, unit_id, UnitType.ROW)
            self.rows.append(new_unit)
            self.units.append(new_unit)
            unit_id += 1

        for region in self.regions:
            self.units.append(region)

        # populate cell_to_units dict
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                self.cell_to_units[(row, col)] = []
                for unit in self.units:
                    if unit.contains(row, col):
                        self.cell_to_units[(row, col)].append(unit)

        # populate cell_to_peers dict
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                self.cell_to_peers[(row, col)] = set()
                for unit in self.cell_to_units[(row, col)]:
                    self.cell_to_peers[(row, col)].update(unit.cell_cords)
                self.cell_to_peers[(row, col)].discard((row, col))

    def get_units_for_cell(self, row: int, col: int) -> list[Unit]:
        return self.cell_to_units[(row, col)]

    def get_peers_for_cell(self, row: int, col: int) -> set[Coordinate]:
        return self.cell_to_peers[(row, col)]
