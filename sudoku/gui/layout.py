"""Screen geometry for the board: where each cell is drawn and which cell a pixel is in.

Pure math, no Qt, so it can be unit tested.
"""

import math
from dataclasses import dataclass

type Coordinate = tuple[int, int]


@dataclass(frozen=True)
class GridLayout:
    """Position and size of the grid inside a widget, in pixels.

    Attributes:
        left: x of the grid's left edge
        top: y of the grid's top edge
        cell: side length of one cell
        n_rows: number of rows
        n_cols: number of columns
    """

    left: float
    top: float
    cell: float
    n_rows: int
    n_cols: int

    @classmethod
    def fit(
        cls, width: float, height: float, n_rows: int, n_cols: int, margin: float = 0.5
    ) -> "GridLayout":
        """Largest grid that fits in width x height, centred, with `margin` cells of space around it."""
        cell = min(width / (n_cols + 2 * margin), height / (n_rows + 2 * margin))
        cell = max(cell, 0.0)
        left = (width - cell * n_cols) / 2
        top = (height - cell * n_rows) / 2
        return cls(left, top, cell, n_rows, n_cols)

    @property
    def width(self) -> float:
        return self.cell * self.n_cols

    @property
    def height(self) -> float:
        return self.cell * self.n_rows

    def cell_rect(self, row: int, col: int) -> tuple[float, float, float, float]:
        """(x, y, width, height) of a cell. Column gives x, row gives y."""
        return (self.left + col * self.cell, self.top + row * self.cell, self.cell, self.cell)

    def cell_at(self, x: float, y: float) -> Coordinate | None:
        """The (row, col) under pixel (x, y), or None if outside the grid."""
        if self.cell <= 0:
            return None
        col = math.floor((x - self.left) / self.cell)
        row = math.floor((y - self.top) / self.cell)
        if 0 <= row < self.n_rows and 0 <= col < self.n_cols:
            return (row, col)
        return None
