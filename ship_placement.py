import random
from typing import List, Tuple
from game_grid import GameGrid


def random_place_ship(
    ship_height: int,
    ship_width: int,
    available_squares: List[List[bool]],
) -> Tuple[int, int]:

    found_ship_placement = False
    while not found_ship_placement:
        row_idx = random.randrange(len(available_squares))
        col_idx = random.randrange(len(available_squares[row_idx]))

        found_ship_placement = True
        for r in range(row_idx, row_idx + ship_height):
            for c in range(col_idx, col_idx + ship_width):
                if (
                    not (
                        0 <= r < len(available_squares)
                        and 0 <= c < len(available_squares[r])
                    )
                    or not available_squares[r][c]
                ):
                    found_ship_placement = False
                    continue

    return row_idx, col_idx


def random_ships_placement(
    ship_dims: List[Tuple[int, int]],
    available_squares: List[List[bool]],
    num_rows: int,
    num_cols: int,
    rotate_allowed: bool = True,
) -> List[Tuple[int, int, int, int]]:
    """
    ship_dims - a list of N ship dimensions: (height, width)
    available_squares - grid of Booleans, where True is a square that is available
    rotate_allowed - if True, the ship dimensions can be switched

    Returns: returns a list of N tuples: (top_row_idx, left_col_idx, ship_height, ship_width)
    """
    available_squares_copy = []
    assert len(available_squares) == num_rows
    for r in range(len(available_squares)):
        assert len(available_squares[r]) == num_cols
        copy_row = []
        for c in range(len(available_squares[r])):
            copy_row.append(available_squares[r][c])
        available_squares_copy.append(copy_row)

    ship_placements = []
    for ship_dim in ship_dims:
        ship_height, ship_width = ship_dim
        if rotate_allowed and random.randint(0, 1) == 1:
            ship_width, ship_height = ship_dim

        top_row_idx, left_col_idx = random_place_ship(
            ship_height, ship_width, available_squares=available_squares_copy
        )
        ship_placements.append((top_row_idx, left_col_idx, ship_height, ship_width))

        bottom_row_idx = top_row_idx + ship_height - 1
        right_col_idx = left_col_idx + ship_width - 1

        top_buffer_row_idx = max(0, top_row_idx - 1)
        bottom_buffer_row_idx = min(num_rows - 1, bottom_row_idx + 1)
        left_buffer_row_idx = max(0, left_col_idx - 1)
        right_buffer_row_idx = min(num_cols - 1, right_col_idx + 1)

        for r in range(top_buffer_row_idx, bottom_buffer_row_idx + 1):
            for c in range(left_buffer_row_idx, right_buffer_row_idx + 1):
                available_squares_copy[r][c] = False

    return ship_placements