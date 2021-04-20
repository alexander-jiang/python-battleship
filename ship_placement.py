import random
import numpy as np
from typing import List, Tuple
from game_grid import GameGrid


ShipPlacement = Tuple[int, int, int, int]


def random_place_ship(
    ship_height: int,
    ship_width: int,
    available_squares: List[List[bool]],
) -> Tuple[int, int]:
    found_ship_placement = False
    while not found_ship_placement:
        row_idx = random.randrange(len(available_squares) - ship_height + 1)
        col_idx = random.randrange(len(available_squares[row_idx]) - ship_width + 1)

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


def get_possible_ship_placements(
    ship_height: int,
    ship_width: int,
    available_squares: List[List[bool]],
) -> List[ShipPlacement]:
    # TODO implement this step with a 2d matrix convolution
    top_left = []
    for top_row_idx in range(len(available_squares) - ship_height + 1):
        for left_col_idx in range(len(available_squares[top_row_idx]) - ship_width + 1):
            top_left.append((top_row_idx, left_col_idx))

    ship_placements = []
    for (row_idx, col_idx) in top_left:
        valid_ship_placement = True
        for r in range(row_idx, row_idx + ship_height):
            for c in range(col_idx, col_idx + ship_width):
                if (
                    not (
                        0 <= r < len(available_squares)
                        and 0 <= c < len(available_squares[r])
                    )
                    or not available_squares[r][c]
                ):
                    valid_ship_placement = False
        if valid_ship_placement:
            ship_placements.append((row_idx, col_idx, ship_height, ship_width))

    return ship_placements


# def get_possible_ship_placements_convolve(
#     ship_height: int,
#     ship_width: int,
#     blocked_squares: np.ndarray,
# ) -> List[ShipPlacement]:
#     k = np.ones((ship_height, ship_width))
#     scipy.ndimage.correlate(available_squares, k, mode="constant", cval=1.0, origin=(-, ))

def random_ships_placement(
    ship_dims: List[Tuple[int, int]],
    available_squares: List[List[bool]],
    num_rows: int,
    num_cols: int,
    rotate_allowed: bool = True,
) -> List[ShipPlacement]:
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

    got_stuck = True
    while got_stuck:
        got_stuck = False

        ship_placements = []
        for ship_dim in ship_dims:
            ship_height, ship_width = ship_dim
            if rotate_allowed and random.randint(0, 1) == 1:
                ship_width, ship_height = ship_dim

            possible_placements = get_possible_ship_placements(
                ship_height, ship_width, available_squares=available_squares_copy
            )
            if len(possible_placements) == 0:
                got_stuck = True
                break

            chosen_placement = random.choice(possible_placements)
            ship_placements.append(chosen_placement)
            top_row_idx, left_col_idx, _, _ = chosen_placement

            bottom_row_idx = top_row_idx + ship_height - 1
            right_col_idx = left_col_idx + ship_width - 1

            top_buffer_row_idx = max(0, top_row_idx - 1)
            bottom_buffer_row_idx = min(num_rows - 1, bottom_row_idx + 1)
            left_buffer_row_idx = max(0, left_col_idx - 1)
            right_buffer_row_idx = min(num_cols - 1, right_col_idx + 1)

            # set the squares (including the ship's buffer) to be unavailable
            for r in range(top_buffer_row_idx, bottom_buffer_row_idx + 1):
                for c in range(left_buffer_row_idx, right_buffer_row_idx + 1):
                    available_squares_copy[r][c] = False
        if len(ship_placements) == len(ship_dims):
            got_stuck = False

    return ship_placements


def main():
    # testing the possible ship placements
    NUM_ROWS = 10
    NUM_COLS = 10

    available_squares = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.bool8)
    available_squares.fill(True)
    available_squares = available_squares.tolist()

    # available_squares[4][4] = False

    # possible_placements = get_possible_ship_placements(
    #     ship_height=5,
    #     ship_width=1,
    #     available_squares=available_squares,
    # )
    # print(possible_placements)

    a = np.array([[1, 2, 0, 0], [5, 3, 0, 4], [0, 0, 0, 7], [9, 3, 0, 0]])
    # note: the weights kernel is "flipped" i.e. as if k = [[0, 0, 1], [0, 1, 1], [1, 1, 1]]
    # see https://stackoverflow.com/q/45152473/2723382
    k = np.array([[1, 1, 1], [1, 1, 0], [1, 0, 0]])
    from scipy import ndimage

    output = ndimage.convolve(a, k, mode="constant", cval=0.0)
    print(output)
    # array([[11, 10, 7, 4], [10, 3, 11, 11], [15, 12, 14, 7], [12, 3, 7, 0]])


if __name__ == "__main__":
    main()