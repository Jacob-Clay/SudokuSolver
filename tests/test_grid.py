from sudoku.grid import Grid, Unit, UnitType
import pytest


@pytest.fixture
def unit_setup():
    coords = {(1, 1), (1, 2), (1, 3)}
    id = 1
    unit_type = UnitType.COLUMN

    return Unit(coords, id, unit_type)


class TestUnit:
    def test_unit_creation(self, unit_setup):
        unit: Unit = unit_setup
        assert unit.type == UnitType.COLUMN
        assert unit.id == 1
        assert unit.coords == {(1, 1), (1, 2), (1, 3)}

    def test_cell_in_unit(self, unit_setup):
        unit = unit_setup
        assert unit.contains(1, 1)
        assert unit.contains(1, 2)
        assert unit.contains(1, 3)

    def test_cell_not_in_unit(self, unit_setup):
        unit = unit_setup
        assert not unit.contains(2, 1)
        assert not unit.contains(3, 1)
        assert not unit.contains(2, 2)


@pytest.fixture
def grid_setup():
    num_rows = 9
    num_cols = 9
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

    return Grid(num_rows, num_cols, regions=regions)


class TestGrid:
    def test_grid_creation(self, grid_setup):
        grid: Grid = grid_setup

        assert grid.n_rows == 9
        assert grid.n_cols == 9
        assert len(grid.regions) == 9

    def test_units_list(self, grid_setup):
        grid: Grid = grid_setup

        num_rows = 0
        num_cols = 0
        num_regions = 0

        for unit in grid.units:
            match unit.type:
                case UnitType.ROW:
                    num_rows += 1
                case UnitType.COLUMN:
                    num_cols += 1
                case UnitType.REGION:
                    num_regions += 1

        assert num_rows == 9
        assert num_cols == 9
        assert num_regions == 9
        assert len(grid.units) == 27  # 9 * 3 (9 cols, 9 rows, 9 regions)

    def test_cell_to_peers(self, grid_setup):
        grid: Grid = grid_setup

        for cell, peers in grid.cell_to_peers.items():
            assert len(peers) == 20
            assert cell not in peers

        assert len(grid.cell_to_peers) == 81

    def test_cell_to_units(self, grid_setup):
        grid: Grid = grid_setup

        for units in grid.cell_to_units.values():
            has_col = False
            has_row = False
            has_region = False
            for unit in units:
                match unit.type:
                    case UnitType.ROW:
                        has_row = True
                    case UnitType.COLUMN:
                        has_col = True
                    case UnitType.REGION:
                        has_region = True

            assert has_col
            assert has_row
            assert has_region
            assert len(units) == 3

        assert len(grid.cell_to_units) == 81

    def test_grid_rows(self, grid_setup):
        grid: Grid = grid_setup

        for unit in grid.rows:
            assert unit.type == UnitType.ROW

        assert len(grid.rows) == 9

    def test_grid_cols(self, grid_setup):
        grid: Grid = grid_setup

        for unit in grid.columns:
            assert unit.type == UnitType.COLUMN

        assert len(grid.columns) == 9
