# SudokuSolver

A Sudoku editor and (work-in-progress) solver written in Python with a PySide6
GUI. The goal is a solver that works the way a person does, step by step,
using the human solving techniques described on
[SudokuWiki](https://www.sudokuwiki.org/Strategy_Families), rather than only
brute-forcing an answer.

## Status

The project is being rewritten. What works today:

- Load a puzzle from an 81-character string
- Enter digits and candidates (pencil marks) in the GUI
- Givens are protected from editing
- Conflicting digits in a row, column or box are highlighted
- Board model with tests, kept separate from the GUI

Planned next (see [TODO.md](TODO.md)):

1. Brute-force solver (also used to check the strategies)
2. Human-style strategies from SudokuWiki, starting with singles,
   pairs and pointing pairs
3. Board sizes other than 9×9 (e.g. 6×6) and irregular (jigsaw) regions

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Installation

```bash
git clone https://github.com/Jacob-Clay/SudokuSolver.git
cd SudokuSolver
uv sync
```

## Usage

### GUI

```bash
uv run python -m sudoku.gui
```

The app opens with an example puzzle. Load your own with **Puzzle → Load from
string** (`Ctrl+O`).

| Key                          | Action                                   |
| ---------------------------- | ---------------------------------------- |
| Click, arrow keys            | Select a cell (arrows wrap around)       |
| `Tab` / `Shift+Tab`          | Next / previous cell                     |
| `1`–`9`                      | Enter a digit                            |
| `Ctrl` + `1`–`9`             | Toggle a candidate (`Cmd` on macOS)      |
| `Delete`, `Backspace` or `0` | Clear the cell                           |
| `Esc`                        | Deselect                                 |
| `Ctrl+O`                     | Load a puzzle from a string              |
| `Ctrl+Shift+C`               | Copy the board as a string               |
| `Ctrl+N`                     | New empty board                          |
| `F11`                        | Toggle full screen                       |

### Puzzle strings

A puzzle is 81 characters, read left to right, top to bottom. Digits `1`–`9`
are givens; `0`, `.`, `_` or `*` mark an empty cell:

```text
300967001040302080020000070070000090000873000500010003004705100905000207800621004
```

### As a library

```python
from sudoku.board import Board

board = Board.from_string(
    "300967001040302080020000070070000090000873000500010003004705100905000207800621004"
)

board.set_cell_value(0, 1, 5)       # rows and columns are 0-based
board.toggle_cell_candidate(0, 2, 8)
print(board.get_conflicts())        # set of (row, col) with duplicate digits
print(board)
```

Editing a given, or using a digit outside 1–9, raises `ValueError`; a
coordinate outside the board raises `IndexError`.

## Project layout

```text
sudoku/
├── grid.py        # board geometry: rows, columns, regions, peers
├── board.py       # cell state and all operations on it
└── gui/           # PySide6 interface (the only part that imports Qt)
tests/             # pytest suite (no Qt needed)
legacy/            # the original version, kept for reference
```

## Development

```bash
uv run python -m pytest   # run the tests
uv run pyright            # type-check (strict on the model)
```

Code conventions (coordinates, numbering, what belongs in which layer) are in
[CONVENTIONS.md](CONVENTIONS.md).

## Contributing

Contributions are welcome:

1. Fork the repository
2. Create a branch: `git checkout -b feature-name`
3. Make your change, with tests, and check that the tests and pyright pass
4. Push the branch and open a pull request against `main`

## Acknowledgements

Solving techniques are based on the strategy guides by Andrew Stuart at
[SudokuWiki.org](https://www.sudokuwiki.org/). This project is an independent
implementation and is not affiliated with that site.

## License

MIT. See [LICENSE](LICENSE).
