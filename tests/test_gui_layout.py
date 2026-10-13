"""Tests for the pixel <-> cell math. No Qt involved."""

import pytest

from sudoku.gui.layout import GridLayout


@pytest.fixture
def layout():
    # 9x9 cells of 50px, grid starting at (25, 25)
    return GridLayout(left=25, top=25, cell=50, n_rows=9, n_cols=9)


def test_fit_centres_and_keeps_cells_square():
    layout = GridLayout.fit(1000, 500, 9, 9, margin=0.5)
    assert layout.cell == 50
    assert layout.top == 25
    assert layout.left == (1000 - 450) / 2


def test_cell_rect_uses_col_for_x_and_row_for_y(layout):
    assert layout.cell_rect(0, 0) == (25, 25, 50, 50)
    assert layout.cell_rect(2, 5) == (25 + 5 * 50, 25 + 2 * 50, 50, 50)


def test_cell_at_corners(layout):
    assert layout.cell_at(25, 25) == (0, 0)
    assert layout.cell_at(25 + 449.9, 25 + 449.9) == (8, 8)


def test_cell_at_row_and_col_not_swapped(layout):
    # far right of the top row
    assert layout.cell_at(25 + 8 * 50 + 10, 25 + 10) == (0, 8)


def test_cell_at_outside_is_none(layout):
    assert layout.cell_at(10, 100) is None
    assert layout.cell_at(100, 10) is None
    assert layout.cell_at(25 + 450, 100) is None
    assert layout.cell_at(100, 25 + 450) is None


def test_every_cell_centre_maps_back(layout):
    for row in range(9):
        for col in range(9):
            x, y, w, h = layout.cell_rect(row, col)
            assert layout.cell_at(x + w / 2, y + h / 2) == (row, col)
