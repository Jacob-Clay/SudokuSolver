from sudoku.grid import Grid, Unit, UnitType
from sudoku.board import Cell


class TestCell:
    def test_cell_creation_default(self):
        cell = Cell()
        assert cell.value == None
        assert cell.candidates == set()
        assert cell.given == False

    def test_cell_with_value(self):
        cell = Cell(value=5)
        assert cell.value == 5

    def test_cell_with_candidates(self):
        cell = Cell(candidates={1, 2, 3})
        assert 1 in cell.candidates
        assert len(cell.candidates) == 3


class TestUnit:
    def test_unit_creation(self):
        cords = {(1, 1), (1, 2), (1, 3)}
        id = 1
        unit_type = UnitType.COLUMN

        unit = Unit(cords, id, unit_type=unit_type)
        assert unit.unit_type == unit_type
        assert unit.unit_id == id
        assert unit.cell_cords == cords

    def test_cell_in_unit(self):
        cords = {(1, 1), (1, 2), (1, 3)}
        id = 1
        unit_type = UnitType.COLUMN

        unit = Unit(cords, id, unit_type=unit_type)
        assert unit.contains(1, 1)
        assert unit.contains(1, 2)
        assert unit.contains(1, 3)

    def test_cell_not_in_unit(self):
        cords = {(1, 1), (1, 2), (1, 3)}
        id = 1
        unit_type = UnitType.COLUMN

        unit = Unit(cords, id, unit_type=unit_type)
        assert not unit.contains(2, 1)
        assert not unit.contains(3, 1)
        assert not unit.contains(2, 2)
