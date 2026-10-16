"""Dataclasses for representing a grid with cells organized into rows, columns, and regions.

This module provides the core data structures for representing
contraint-satisfaction grids (sudoku puzzles). Each cell belongs to exactly one
row, one column, and one region. Cells in the same unit (row, column, or region)
are considered peers.
"""

from dataclasses import dataclass, field
from enum import Enum

type Coordinate = tuple[int, int]


class UnitType(Enum):
    """Enumeration of the three types of units in a grid.

    Attributes:
        ROW: A horizontal line of cells spanning all columns.
        COLUMN: A vertical line of cells spanning all rows.
        REGION: A custom grouping of cells (e.g., a 3x3 box in standard Sudoku).
    """

    ROW = "row"
    COLUMN = "column"
    REGION = "region"


@dataclass(frozen=True)
class Unit:
    """A collection of cells that form a logical unit.

    A unit is an immutable group of cells that must satisfy some constraint

    Attributes:
        coords: The set of cell coordinates in this unit.
        id: A unique identifier for this unit within its type.
        type: The type of unit (ROW, COLUMN, or REGION).
    """

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
    """A grid with cells organized into rows, columns, and regions.

    A grid precomputes the structure of rows, columns, regions, and peer
    relationships to enable efficient constraint satisfaction solving. All cells
    must be covered by exactly one region.

    Attributes:
        n_rows: The number of rows in the grid. Must be positive
        n_cols: The number of columns in the grid. Must be positive
        regions: A list of regions partitioning the grid. Must cover all cells
        exactly once.
        columns: All column units, indexed by column number (derived).
        rows: All row units, indexed by row number (derived).
        units: All units (rows, columns, and regions combined) (derived).
        cell_to_peers: Mapping from each cell to its three units (row, column,
        region) (derived).
        cell_to_units: Mapping from each cell to all peer cells (derived).

    Raises:
        ValueError: if n_rows or n_cols is non-positive, if regions don't
        partition the grid, or if any region is not of type REGION.
    """

    n_rows: int
    n_cols: int
    regions: tuple[Unit, ...]
    columns: tuple[Unit, ...] = field(init=False, default_factory=tuple[Unit])
    rows: tuple[Unit, ...] = field(init=False, default_factory=tuple[Unit])
    units: tuple[Unit, ...] = field(init=False, default_factory=tuple[Unit])
    cell_to_peers: frozenset[tuple[Coordinate, frozenset[Coordinate]]] = field(
        init=False, default_factory=frozenset[tuple[Coordinate, frozenset[Coordinate]]]
    )
    cell_to_units: frozenset[tuple[Coordinate, tuple[Unit, ...]]] = field(
        init=False, default_factory=frozenset[tuple[Coordinate, tuple[Unit, ...]]]
    )

    def __post_init__(self) -> None:
        """Validate the grid and precompute derived structures.

        Raises:
            ValueError: If grid dimensions are invalid, regions don't
            partition the grid, or if any region is not of type REGION.
        """
        # check if n_rows and n_cols are valid
        if self.n_rows <= 0 or self.n_cols <= 0:
            raise ValueError("n_rows and n_cols must be positive")

        cols: list[Unit] = []
        rows: list[Unit] = []
        units: list[Unit] = []
        cells: frozenset[Coordinate]
        new_unit: Unit
        for col in range(self.n_cols):
            cells = frozenset({(row, col) for row in range(self.n_rows)})
            new_unit = Unit(cells, col, UnitType.COLUMN)
            cols.append(new_unit)
            units.append(new_unit)

        for row in range(self.n_rows):
            cells = frozenset({(row, col) for col in range(self.n_cols)})
            new_unit = Unit(cells, row, UnitType.ROW)
            rows.append(new_unit)
            units.append(new_unit)

        units.extend(self.regions)

        # check if regions are valid
        for region in self.regions:
            if region.type != UnitType.REGION:
                raise ValueError("non valid regions. must be of REGION type")
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                n_regions_containing_cell: int = 0
                for region in self.regions:
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
        object.__setattr__(self, "columns", tuple(cols))
        object.__setattr__(self, "rows", tuple(rows))
        object.__setattr__(self, "units", tuple(units))

        # for dicts, convert to frozenset of (key, value) pairs
        object.__setattr__(
            self,
            "cell_to_units",
            frozenset(
                (coord, tuple(units_list))
                for coord, units_list in cell_to_units.items()
            ),
        )
        object.__setattr__(
            self,
            "cell_to_peers",
            frozenset(
                (coord, frozenset(peers)) for coord, peers in cell_to_peers.items()
            ),
        )

    def get_units_for_cell(self, row: int, col: int) -> tuple[Unit, ...]:
        """Get all units containing a cell.

        Args:
            row: the row index of the cell.
            col: the column index of the cell.

        Returns:
            A list of the three units (row, column, region) containing the cell.
        """
        coord: Coordinate = (row, col)
        return next(
            (units for c, units in self.cell_to_units if c == coord),
            tuple[Unit, ...](),
        )

    def get_peers_for_cell(self, row: int, col: int) -> frozenset[Coordinate]:
        """Get all peer cells (cells in the same unit).

        Args:
            row: the row index of the cell.
            col: the column index of the cell.

        Returns:
            A set of coordinates for all cells that share a unit with the given
            cell, excluding the cell itself.
        """
        coord: Coordinate = (row, col)
        return next(
            (peers for c, peers in self.cell_to_peers if c == coord),
            frozenset[Coordinate](),
        )
