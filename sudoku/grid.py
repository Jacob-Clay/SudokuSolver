"""All needed dataclasses for a grid of cells including their regions."""

from dataclasses import dataclass, field
from enum import Enum

type Coordinate = tuple[int, int]


class UnitType(Enum):
    ROW = "row"
    COLUMN = "column"
    REGION = "region"


@dataclass(frozen=True)
class Unit:
    coords: frozenset[Coordinate]
    id: int
    type: UnitType

    def contains(self, row: int, col: int) -> bool:
        """Check if this unit contains a cell.

        Args:
            row: the row of the cell to check
            col: the column of the cell to check

        Returns:
            True if in region, else False
        """
        return (row, col) in self.coords


@dataclass(frozen=True)
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

        # check if n_rows and n_cols are valid
        if self.n_rows <= 0 or self.n_cols <= 0:
            raise ValueError("n_rows and n_cols must be positive")

        cols: list[Unit] = []
        rows: list[Unit] = []
        units: list[Unit] = []
        for col in range(self.n_cols):
            cells: frozenset[Coordinate] = frozenset(
                {(row, col) for row in range(self.n_rows)}
            )
            new_unit = Unit(cells, col, UnitType.COLUMN)
            cols.append(new_unit)
            units.append(new_unit)

        for row in range(self.n_rows):
            cells: frozenset[Coordinate] = frozenset(
                {(row, col) for col in range(self.n_cols)}
            )
            new_unit = Unit(cells, row, UnitType.ROW)
            rows.append(new_unit)
            units.append(new_unit)

        units.extend(self.regions)

        # check if regions are valid
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                n_regions_containing_cell: int = 0
                for region in self.regions:
                    if region.type != UnitType.REGION:
                        raise ValueError("non valid regions. must be of REGION type")
                    if (row, col) in region.coords:
                        n_regions_containing_cell += 1
                if n_regions_containing_cell != 1:
                    raise ValueError(
                        "non valid regions. all cells must be in exactly 1 region"
                    )

        cell_to_units: dict[Coordinate, list[Unit]] = {}
        # populate cell_to_units dict
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                cell_to_units[(row, col)] = []
                for unit in units:
                    if unit.contains(row, col):
                        cell_to_units[(row, col)].append(unit)

        cell_to_peers: dict[Coordinate, set[Coordinate]] = {}
        # populate cell_to_peers dict
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                cell_to_peers[(row, col)] = set()
                for unit in cell_to_units[(row, col)]:
                    cell_to_peers[(row, col)].update(unit.coords)
                cell_to_peers[(row, col)].discard((row, col))

        # set the items
        object.__setattr__(self, "columns", cols)
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "units", units)
        object.__setattr__(self, "cell_to_units", cell_to_units)
        object.__setattr__(self, "cell_to_peers", cell_to_peers)

    def get_units_for_cell(self, row: int, col: int) -> list[Unit]:
        return self.cell_to_units[(row, col)]

    def get_peers_for_cell(self, row: int, col: int) -> set[Coordinate]:
        return self.cell_to_peers[(row, col)]
