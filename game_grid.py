from typing import Optional, List


class GameGrid:
    def __init__(
        self,
        num_rows: int,
        num_cols: int,
        initial_value: Optional,
    ):
        grid = []
        for row_idx in range(num_rows):
            grid_row = []
            for col_idx in range(num_cols):
                grid_row.append(initial_value)
            grid.append(grid_row)
        self._grid = grid
        self._num_rows = num_rows
        self._num_cols = num_cols

    def __repr__(self):
        return self._grid.__repr__()

    @property
    def grid(self) -> List[List]:
        return self._grid

    def are_indexes_valid(self, row_idx: int, col_idx: int) -> bool:
        return (0 <= row_idx < self._num_rows) and (0 <= col_idx < self._num_cols)

    def _check_indexes(self, row_idx: int, col_idx: int):
        assert (
            0 <= row_idx < self._num_rows
        ), f"Error! Row index {row_idx} is out of bounds!"
        assert (
            0 <= col_idx < self._num_cols
        ), f"Error! Column index {col_idx} is out of bounds!"

    def read_grid(self, row_idx: int, col_idx: int):
        self._check_indexes(row_idx, col_idx)
        return self._grid[row_idx][col_idx]

    def update_grid(self, row_idx: int, col_idx: int, new_value):
        self._check_indexes(row_idx, col_idx)
        self._grid[row_idx][col_idx] = new_value

    def update_entire_grid(self, new_values: List[List]):
        new_grid = []
        assert (
            len(new_values) == self._num_rows
        ), f"Update entire grid error: incorrect number of rows"
        for row_idx in range(len(new_values)):
            row = new_values[row_idx]
            assert (
                len(row) == self._num_cols
            ), f"Update entire grid error: incorrect number of columns in row index {row_idx}"
            new_row = []
            for new_value in row:
                new_row.append(row)
            new_grid.append(new_row)
        self._grid = new_grid