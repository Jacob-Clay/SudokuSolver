# Conventions

Rules this codebase follows. If code and this file disagree, one of them is wrong — fix it.

## Coordinates

- A cell is identified by a `Coordinate`: a `(row, col)` tuple. Always row first.
- Rows and columns are numbered **0–8** in code. Row 0 is the top, column 0 is the left.
- Human-readable labels (GUI, solver explanations, test messages) count from **1**:
  `(0, 0)` is shown as "r1c1". Add 1 only when building a label, never in the logic.

## Digits and candidates

- Digits are `int` 1–9. Never strings.
- An empty cell has `value = None`. `0` is never stored as a value.
- Candidates are a `set[int]`. An empty set means "no candidates recorded".
- Centre marks entered by the player are treated as candidates.
- **TODO — decide:** when a value is placed in a cell, are its candidates cleared or kept?

## Givens

- `given = True` means the digit was part of the original puzzle.
- A given cannot be changed or cleared by normal editing. `Board` enforces this, not `Cell`.

## Units

- A unit is a row, a column or a region (box). Every standard cell is in exactly 3 units.
- Each unit has a `UnitType` (`ROW`, `COLUMN`, `REGION`) and an id.
- Unit ids are numbered **0-8** within their type, like coordinates.
  The label is built from both: "row 4", "column 7", "region 5" (id + 1).
- Regions are numbered left to right, top to bottom: region 1 is the top-left box.
- Regions are an input to `Grid`, so irregular (jigsaw) layouts are possible.
  A layout is valid only if every cell is in exactly one region.
- Peers are all cells sharing at least one unit with a cell, excluding the cell itself
  (20 in a standard grid).

## Stored vs derived state

- Store only what cannot be recalculated: value, candidates, given.
- Anything that can be calculated is a method, not a field.
  Examples: conflicts/duplicates, "is the board solved", candidate counts.

## Layers

- `grid.py`: geometry only (units, peers). Immutable after creation. No cells, no Qt.
- `board.py`: cell state and operations on it. No Qt.
- Formats (81-char string, 162-char SudokuWiki string, Sudoku Maker JSON) are separate
  import/export adapters. Their quirks stay in the adapter:
  - Sudoku Maker spells it `centremarks`, uses `[row][col]`, stores values as ints,
    and has `pencilMarks` (corner marks).
- Solver and strategies operate on a `Board`. No Qt.
- Only the GUI imports PySide6.

## Code style

- Classes are `CapitalizedNames`, functions and variables are `snake_case`.
- Compare with `None` using `is` / `is not`.
- Requires Python 3.14+ (for the `type` statement).

## Tests

- pytest. Test files are `tests/test_*.py`, test functions start with `test_`.
- Run from the project root with `python -m pytest`.
- Tests never import PySide6.
