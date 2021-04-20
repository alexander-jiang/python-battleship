from tabulate import tabulate
from game_grid import GameGrid
from typing import Optional, List, Tuple

from ship_placement import random_ships_placement


SHIP_LOCATION_EMPTY = 0
LOCATION_NOT_GUESSED = None
LOCATION_GUESS_MISS = False
LOCATION_GUESS_HIT = True
STANDARD_SHIP_DIMENSIONS = [(5, 1), (4, 1), (3, 1), (3, 1), (2, 1)]


class BattleshipGameState:
    def __init__(
        self,
        num_rows: int = 10,
        num_cols: int = 10,
        is_my_turn: bool = True,
        our_ship_locations: Optional[List[List]] = None,
        opponent_ship_locations: Optional[List[List]] = None,
        our_guesses: Optional[List[List]] = None,
        opponent_guesses: Optional[List[List]] = None,
        ships_dimensions: Optional[List[Tuple[int, int]]] = None,
    ):
        self.is_my_turn = is_my_turn
        self.is_game_over = False
        self.num_rows = num_rows
        self.num_cols = num_cols

        self.our_ship_locations = GameGrid(
            num_rows=num_rows, num_cols=num_cols, initial_value=SHIP_LOCATION_EMPTY
        )
        if our_ship_locations is not None:
            self.our_ship_locations.update_entire_grid(our_ship_locations)
        self.opponent_ship_locations = GameGrid(
            num_rows=num_rows, num_cols=num_cols, initial_value=SHIP_LOCATION_EMPTY
        )
        if opponent_ship_locations is not None:
            self.opponent_ship_locations.update_entire_grid(opponent_ship_locations)

        self.our_guesses = GameGrid(
            num_rows=num_rows, num_cols=num_cols, initial_value=LOCATION_NOT_GUESSED
        )
        if our_guesses is not None:
            self.our_guesses.update_entire_grid(our_guesses)
        self.opponent_guesses = GameGrid(
            num_rows=num_rows, num_cols=num_cols, initial_value=LOCATION_NOT_GUESSED
        )
        if opponent_guesses is not None:
            self.opponent_guesses.update_entire_grid(opponent_guesses)

        # track which ships are still alive for us and our opponent
        if ships_dimensions is None:
            ship_dimensions_to_use = STANDARD_SHIP_DIMENSIONS
        else:
            ship_dimensions_to_use = ships_dimensions

        # lists of tuples: ship value in the grid, and the dimensions of the ship
        self.our_ships = []
        self.opponent_ships = []
        next_ship_number = 1
        for ship_dims in ship_dimensions_to_use:
            self.our_ships.append((next_ship_number, ship_dims))
            self.opponent_ships.append((next_ship_number, ship_dims))
            next_ship_number += 1

        self.ships_placed = self.check_placements_ready()

    def place_ship(
        self,
        top_row_idx: int,
        left_col_idx: int,
        ship_width: int,
        ship_height: int,
        ship_value,
        is_our_ship: bool,
    ) -> bool:
        # ship dimensions must not be 0
        assert ship_width > 0 and ship_height > 0

        # check that (ship value, ship dims) match the expected ship values
        if is_our_ship and (
            (ship_value, (ship_height, ship_width)) not in self.our_ships
            and (ship_value, (ship_width, ship_height)) not in self.our_ships
        ):
            return False
        elif not is_our_ship and (
            (ship_value, (ship_height, ship_width)) not in self.opponent_ships
            and (ship_value, (ship_width, ship_height)) not in self.opponent_ships
        ):
            return False

        # if the ship wasn't already placed, clear its old position first before placing again
        if is_our_ship and self._is_valid_ship_placement(
            self.our_ship_locations, ship_value, (ship_height, ship_width)
        ):
            self.clear_ship_placement(
                self.our_ship_locations, ship_value, (ship_height, ship_width)
            )
        elif not is_our_ship and self._is_valid_ship_placement(
            self.opponent_ship_locations, ship_value, (ship_height, ship_width)
        ):
            self.clear_ship_placement(
                self.opponent_ship_locations, ship_value, (ship_height, ship_width)
            )

        # check if the ship placement overlaps with a buffer! (can do neighboring check for each)
        bottom_row_idx = top_row_idx + ship_height - 1
        right_col_idx = left_col_idx + ship_width - 1

        # check if ship placement has an invalid coordinates
        for row_idx in range(top_row_idx, bottom_row_idx + 1):
            for col_idx in range(left_col_idx, right_col_idx + 1):
                if is_our_ship and not self.our_ship_locations.are_indexes_valid(
                    row_idx, col_idx
                ):
                    return False
                elif (
                    not is_our_ship
                    and not self.opponent_ship_locations.are_indexes_valid(
                        row_idx, col_idx
                    )
                ):
                    return False

        top_buffer_row_idx = max(0, top_row_idx - 1)
        bottom_buffer_row_idx = min(self.num_rows - 1, bottom_row_idx + 1)
        left_buffer_row_idx = max(0, left_col_idx - 1)
        right_buffer_row_idx = min(self.num_cols - 1, right_col_idx + 1)
        for row_idx in range(top_buffer_row_idx, bottom_buffer_row_idx + 1):
            for col_idx in range(left_buffer_row_idx, right_buffer_row_idx + 1):
                if is_our_ship:
                    ship_loc_value = self.our_ship_locations.read_grid(row_idx, col_idx)
                else:
                    ship_loc_value = self.opponent_ship_locations.read_grid(
                        row_idx, col_idx
                    )

                if ship_loc_value != SHIP_LOCATION_EMPTY:
                    # can't place ship because another ship is overlapping with the buffer
                    return False

        # now that the ship placement is verified, we can safely update the locations grid
        for row_idx in range(top_row_idx, bottom_row_idx + 1):
            for col_idx in range(left_col_idx, right_col_idx + 1):
                if is_our_ship:
                    self.our_ship_locations.update_grid(
                        row_idx, col_idx, new_value=ship_value
                    )
                else:
                    self.opponent_ship_locations.update_grid(
                        row_idx, col_idx, new_value=ship_value
                    )

        self.ships_placed = self.check_placements_ready()
        return True

    def check_placements_ready(self) -> bool:
        # not only check if placements are valid, but check that both players have placed all available ships
        for ship_value, ship_dims in self.our_ships:
            if not self._is_valid_ship_placement(
                self.our_ship_locations, ship_value, ship_dims
            ):
                return False
        for ship_value, ship_dims in self.opponent_ships:
            if not self._is_valid_ship_placement(
                self.opponent_ship_locations, ship_value, ship_dims
            ):
                return False
        return True

    def _is_valid_ship_placement(
        self, ship_locations_grid: GameGrid, ship_value, ship_dims: Tuple[int, int]
    ):
        # ship dimensions must not be 0
        assert ship_dims[0] > 0 and ship_dims[1] > 0

        # make sure the ship is located, and the dimensions match
        # 1. check the count of locations vs. dimensions
        # 2. check the bounds of dimensions (min and max, x and y)
        min_row_idx, max_row_idx = None, None
        min_col_idx, max_col_idx = None, None
        count_ship_value = 0
        for row_idx in range(self.num_rows):
            for col_idx in range(self.num_cols):
                if ship_locations_grid.read_grid(row_idx, col_idx) == ship_value:
                    count_ship_value += 1
                    if min_row_idx is None or row_idx < min_row_idx:
                        min_row_idx = row_idx
                    if max_row_idx is None or row_idx > max_row_idx:
                        max_row_idx = row_idx
                    if min_col_idx is None or col_idx < min_col_idx:
                        min_col_idx = col_idx
                    if max_col_idx is None or col_idx > max_col_idx:
                        max_col_idx = col_idx

        # make sure the correct number of squares are labeled as the ship and the dimension boundaries match
        return ship_dims[0] * ship_dims[1] == count_ship_value and (
            (
                max_row_idx - min_row_idx + 1 == ship_dims[0]
                and max_col_idx - min_col_idx + 1 == ship_dims[1]
            )
            or (
                max_row_idx - min_row_idx + 1 == ship_dims[1]
                and max_col_idx - min_col_idx + 1 == ship_dims[0]
            )
        )

    def clear_ship_placement(
        self, locations_grid: GameGrid, ship_value, ship_dims: Tuple[int, int]
    ):
        print(f"clearing ship placement: value = {ship_value}, dims = {ship_dims}")
        for row_idx in range(self.num_rows):
            for col_idx in range(self.num_cols):
                if locations_grid.read_grid(row_idx, col_idx) == ship_value:
                    locations_grid.update_grid(
                        row_idx, col_idx, new_value=SHIP_LOCATION_EMPTY
                    )

    def clear_all_ship_placements(self, locations_grid: GameGrid):
        for row_idx in range(self.num_rows):
            for col_idx in range(self.num_cols):
                locations_grid.update_grid(
                    row_idx, col_idx, new_value=SHIP_LOCATION_EMPTY
                )

    def randomize_ship_placements(
        self,
        ship_dims: List[Tuple[int, int]],
        our_ships: bool,
    ):
        available_squares = []
        for r in range(self.num_rows):
            row = []
            for c in range(self.num_cols):
                row.append(True)
            available_squares.append(row)
        random_ship_placements = random_ships_placement(
            ship_dims,
            available_squares=available_squares,
            num_rows=self.num_rows,
            num_cols=self.num_cols,
            rotate_allowed=True,
        )
        for idx in range(len(random_ship_placements)):
            ship_placement = random_ship_placements[idx]
            top_row_idx, left_col_idx, ship_height, ship_width = ship_placement
            self.place_ship(
                top_row_idx=top_row_idx,
                left_col_idx=left_col_idx,
                ship_width=ship_width,
                ship_height=ship_height,
                ship_value=idx + 1,
                is_our_ship=our_ships,
            )
            print(
                f"placed ship {idx + 1}, dims {ship_height}, {ship_width} at {top_row_idx}, {left_col_idx}"
            )

    def rotate_ship_placement(self, locations_grid: GameGrid, ship_value) -> bool:
        """
        Rotate the ship around its top left corner.
        Returns False if the rotation isn't possible (and doesn't change the game state).
        """
        min_row_idx, max_row_idx = None, None
        min_col_idx, max_col_idx = None, None
        count_ship_value = 0
        for row_idx in range(self.num_rows):
            for col_idx in range(self.num_cols):
                if locations_grid.read_grid(row_idx, col_idx) == ship_value:
                    count_ship_value += 1
                    if min_row_idx is None or row_idx < min_row_idx:
                        min_row_idx = row_idx
                    if max_row_idx is None or row_idx > max_row_idx:
                        max_row_idx = row_idx
                    if min_col_idx is None or col_idx < min_col_idx:
                        min_col_idx = col_idx
                    if max_col_idx is None or col_idx > max_col_idx:
                        max_col_idx = col_idx

        ship_width, ship_height = (
            max_col_idx - min_col_idx + 1,
            max_row_idx - min_row_idx + 1,
        )
        self.clear_ship_placement(
            locations_grid, ship_value, ship_dims=(ship_width, ship_height)
        )

        rotate_success = self.place_ship(
            min_row_idx,
            min_col_idx,
            ship_width=ship_height,
            ship_height=ship_width,
            ship_value=ship_value,
            is_our_ship=True,
        )
        if not rotate_success:
            self.place_ship(
                min_row_idx,
                min_col_idx,
                ship_width=ship_width,
                ship_height=ship_height,
                ship_value=ship_value,
                is_our_ship=True,
            )
            return False
        else:
            return True

    def check_ship_alive(
        self, locations_grid: GameGrid, opponents_guesses_grid: GameGrid, ship_value
    ):
        assert ship_value != SHIP_LOCATION_EMPTY
        for row_idx in range(self.num_rows):
            for col_idx in range(self.num_cols):
                if (
                    locations_grid.read_grid(row_idx, col_idx) == ship_value
                    and opponents_guesses_grid.read_grid(row_idx, col_idx)
                    != LOCATION_GUESS_HIT
                ):
                    return True
        return False

    def any_ships_alive(
        self, locations_grid: GameGrid, opponents_guesses_grid: GameGrid
    ):
        for row_idx in range(self.num_rows):
            for col_idx in range(self.num_cols):
                if (
                    locations_grid.read_grid(row_idx, col_idx) != SHIP_LOCATION_EMPTY
                    and opponents_guesses_grid.read_grid(row_idx, col_idx)
                    != LOCATION_GUESS_HIT
                ):
                    return True
        return False

    def get_player_home_grid(self) -> List[List]:
        grid_symbols = []
        for row_idx in range(self.num_rows):
            grid_row = []
            for col_idx in range(self.num_cols):
                ship_loc_value = self.our_ship_locations.read_grid(row_idx, col_idx)
                opponent_guess_value = self.opponent_guesses.read_grid(row_idx, col_idx)
                grid_symbol = " "
                if ship_loc_value != SHIP_LOCATION_EMPTY:
                    # check if opponent has struck our ship here:
                    if opponent_guess_value == LOCATION_GUESS_HIT:
                        # check if the ship is sunk
                        if self.check_ship_alive(
                            self.our_ship_locations,
                            self.opponent_guesses,
                            ship_loc_value,
                        ):
                            grid_symbol = "X"
                        else:
                            grid_symbol = "S"
                    else:
                        grid_symbol = str(ship_loc_value)
                else:
                    # check if opponent has missed here
                    if opponent_guess_value == LOCATION_GUESS_MISS:
                        grid_symbol = "."
                grid_row.append(grid_symbol)
            grid_symbols.append(grid_row)
        return grid_symbols

    def get_player_tracking_grid(self) -> List[List]:
        grid_symbols = []
        for row_idx in range(self.num_rows):
            grid_row = []
            for col_idx in range(self.num_cols):
                guess_value = self.our_guesses.read_grid(row_idx, col_idx)
                grid_symbol = " "
                if guess_value == LOCATION_GUESS_HIT:
                    # check if we struck a ship here:
                    ship_loc_value = self.opponent_ship_locations.read_grid(
                        row_idx, col_idx
                    )
                    assert ship_loc_value != SHIP_LOCATION_EMPTY
                    # check if the ship is sunk
                    if self.check_ship_alive(
                        self.opponent_ship_locations,
                        self.our_guesses,
                        ship_loc_value,
                    ):
                        grid_symbol = "X"
                    else:
                        grid_symbol = "S"
                elif guess_value == LOCATION_GUESS_MISS:
                    grid_symbol = "."
                grid_row.append(grid_symbol)
            grid_symbols.append(grid_row)
        return grid_symbols

    def is_game_over(self):
        return self.any_ships_alive(
            self.our_ship_locations, self.opponent_guesses
        ) or self.any_ships_alive(self.opponent_ship_locations, self.our_guesses)

    def attempt_strike(
        self,
        struck_locations_grid: GameGrid,
        strikers_guesses_grid: GameGrid,
        square_row_idx: int,
        square_col_idx: int,
    ) -> bool:
        """ Returns True if the guess hit a ship """
        # Did the guess hit a ship? (check struck_locations_grid)
        if (
            struck_locations_grid.read_grid(square_row_idx, square_col_idx)
            == SHIP_LOCATION_EMPTY
        ):
            # The guess missed! (update strikers_guesses_grid with a miss)
            strikers_guesses_grid.update_grid(
                square_row_idx, square_col_idx, LOCATION_GUESS_MISS
            )
            return False

        # The guess hit! (update strikers_guesses_grid with a hit)
        strikers_guesses_grid.update_grid(
            square_row_idx, square_col_idx, LOCATION_GUESS_HIT
        )
        # Did the hit sink a ship? (check struck_locations_grid again)
        ship_that_was_hit = struck_locations_grid.read_grid(
            square_row_idx, square_col_idx
        )
        if not self.check_ship_alive(
            struck_locations_grid, strikers_guesses_grid, ship_that_was_hit
        ):
            # The guess sunk an ship!
            # TODO update the struck player's alive ships

            # Did the guess end the game?
            if not self.any_ships_alive(struck_locations_grid, strikers_guesses_grid):
                print("game is now over!")
                self.is_game_over = True
        return True

    def call_square(self, square_row_idx: int, square_col_idx: int) -> bool:
        """ Returns True if the guess hit a ship """
        if self.is_my_turn:
            did_hit = self.attempt_strike(
                self.opponent_ship_locations,
                self.our_guesses,
                square_row_idx,
                square_col_idx,
            )
        else:
            did_hit = self.attempt_strike(
                self.our_ship_locations,
                self.opponent_guesses,
                square_row_idx,
                square_col_idx,
            )

        # if the guess missed, then the turn passes to the other player
        if not did_hit and not self.is_game_over:
            self.is_my_turn = not self.is_my_turn
        return did_hit


def main():
    # CLASS_NAME() calls __init__() method (i.e. the "constructor")
    game_state = BattleshipGameState()


if __name__ == "__main__":
    main()
