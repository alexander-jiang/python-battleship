import pytest

from game_state import BattleshipGameState, SHIP_LOCATION_EMPTY
from game_grid import GameGrid


def _check_all_grid_squares_equal(grid: GameGrid, expected_value):
    for row_idx in range(grid.num_rows):
        for col_idx in range(grid.num_rows):
            assert grid.read_grid(row_idx, col_idx) == expected_value


def _check_rectangular_region_values(
    grid: GameGrid,
    top_row_idx: int,
    left_col_idx: int,
    height: int,
    width: int,
    region_value,
    other_value,
):
    for row_idx in range(grid.num_rows):
        for col_idx in range(grid.num_rows):
            if (
                top_row_idx <= row_idx < top_row_idx + height
                and left_col_idx <= col_idx < left_col_idx + width
            ):
                assert grid.read_grid(row_idx, col_idx) == region_value
            else:
                assert grid.read_grid(row_idx, col_idx) == other_value


def test_ship_placement():
    game_state = BattleshipGameState()

    ship1_row_idx, ship1_col_idx = 1, 2
    ship1_height, ship1_width = 3, 1
    ship1_value = 1

    # ship placement should not report error
    assert game_state.place_ship(
        ship1_row_idx,
        ship1_col_idx,
        ship1_width,
        ship1_height,
        ship1_value,
        is_our_ship=True,
    )

    # make sure ship is placed correctly (only affecting the specified squares)
    _check_rectangular_region_values(
        grid=game_state.our_ship_locations,
        top_row_idx=ship1_row_idx,
        left_col_idx=ship1_col_idx,
        height=ship1_height,
        width=ship1_width,
        region_value=ship1_value,
        other_value=SHIP_LOCATION_EMPTY,
    )

    # make sure the opponent's ship locations grid is not affected
    _check_all_grid_squares_equal(
        game_state.opponent_ship_locations, SHIP_LOCATION_EMPTY
    )

    opp_ship1_row_idx, opp_ship1_col_idx = 2, 0
    opp_ship1_height, opp_ship1_width = 1, 3
    opp_ship1_value = 1

    # opponent's ship placement should not report error
    assert game_state.place_ship(
        opp_ship1_row_idx,
        opp_ship1_col_idx,
        opp_ship1_width,
        opp_ship1_height,
        opp_ship1_value,
        is_our_ship=False,
    )

    # make sure ship is placed correctly (only affecting the specified squares)
    _check_rectangular_region_values(
        grid=game_state.opponent_ship_locations,
        top_row_idx=opp_ship1_row_idx,
        left_col_idx=opp_ship1_col_idx,
        height=opp_ship1_height,
        width=opp_ship1_width,
        region_value=opp_ship1_value,
        other_value=SHIP_LOCATION_EMPTY,
    )

    # make sure the players's ship locations grid is not affected
    _check_rectangular_region_values(
        grid=game_state.our_ship_locations,
        top_row_idx=ship1_row_idx,
        left_col_idx=ship1_col_idx,
        height=ship1_height,
        width=ship1_width,
        region_value=ship1_value,
        other_value=SHIP_LOCATION_EMPTY,
    )


def test_ship_placement_bounds():
    game_state = BattleshipGameState()

    ship1_row_idx, ship1_col_idx = 5, 8
    ship1_height, ship1_width = 5, 1
    ship1_value = 1

    # ship placement should report error (ship placement above top edge)
    assert not game_state.place_ship(
        -2,
        4,
        ship1_width,
        ship1_height,
        ship1_value,
        is_our_ship=True,
    )
    _check_all_grid_squares_equal(game_state.our_ship_locations, SHIP_LOCATION_EMPTY)
    _check_all_grid_squares_equal(
        game_state.opponent_ship_locations, SHIP_LOCATION_EMPTY
    )

    # ship placement should report error (ship placement below bottom edge)
    assert not game_state.place_ship(
        6,
        4,
        ship1_width,
        ship1_height,
        ship1_value,
        is_our_ship=True,
    )
    _check_all_grid_squares_equal(game_state.our_ship_locations, SHIP_LOCATION_EMPTY)
    _check_all_grid_squares_equal(
        game_state.opponent_ship_locations, SHIP_LOCATION_EMPTY
    )

    ship2_row_idx, ship2_col_idx = 3, 6
    ship2_height, ship2_width = 1, 4
    ship2_value = 2

    # ship placement should report error (ship placement over left edge)
    assert not game_state.place_ship(
        2,
        -4,
        ship1_width,
        ship1_height,
        ship1_value,
        is_our_ship=True,
    )
    _check_all_grid_squares_equal(game_state.our_ship_locations, SHIP_LOCATION_EMPTY)
    _check_all_grid_squares_equal(
        game_state.opponent_ship_locations, SHIP_LOCATION_EMPTY
    )

    # ship placement should report error (ship placement over right edge)
    assert not game_state.place_ship(
        9,
        7,
        ship1_width,
        ship1_height,
        ship1_value,
        is_our_ship=True,
    )
    _check_all_grid_squares_equal(game_state.our_ship_locations, SHIP_LOCATION_EMPTY)
    _check_all_grid_squares_equal(
        game_state.opponent_ship_locations, SHIP_LOCATION_EMPTY
    )

    # these ship placements are valid:
    assert game_state.place_ship(
        ship1_row_idx,
        ship1_col_idx,
        ship1_width,
        ship1_height,
        ship1_value,
        is_our_ship=True,
    )
    _check_rectangular_region_values(
        grid=game_state.our_ship_locations,
        top_row_idx=ship1_row_idx,
        left_col_idx=ship1_col_idx,
        height=ship1_height,
        width=ship1_width,
        region_value=ship1_value,
        other_value=SHIP_LOCATION_EMPTY,
    )

    assert game_state.place_ship(
        ship2_row_idx,
        ship2_col_idx,
        ship2_width,
        ship2_height,
        ship2_value,
        is_our_ship=True,
    )

    # TODO check that the both ship's squares are set
    
    

def test_ship_placement_collision():
    game_state = BattleshipGameState()

    ship1_row_idx, ship1_col_idx = 4, 5
    ship1_height, ship1_width = 5, 1
    ship1_value = 1

    ship2_row_idx, ship2_col_idx = 3, 6
    ship2_height, ship2_width = 1, 4
    ship2_value = 2

    # place initial ship
    assert game_state.place_ship(
        ship1_row_idx,
        ship1_col_idx,
        ship1_width,
        ship1_height,
        ship1_value,
        is_our_ship=True,
    )

    # this ship placement is invalid: collision with existing ship on square (4, 5)
    assert not game_state.place_ship(
        4,
        2,
        ship2_width,
        ship2_height,
        ship2_value,
        is_our_ship=True,
    )

    # check that only the original ship's squares are set
    _check_rectangular_region_values(
        grid=game_state.our_ship_locations,
        top_row_idx=ship1_row_idx,
        left_col_idx=ship1_col_idx,
        height=ship1_height,
        width=ship1_width,
        region_value=ship1_value,
        other_value=SHIP_LOCATION_EMPTY,
    )


    # this ship placement is invalid: collision with existing ship on square (6, 5)
    assert not game_state.place_ship(
        6,
        3,
        ship2_width,
        ship2_height,
        ship2_value,
        is_our_ship=True,
    )

    # check that only the original ship's squares are set
    _check_rectangular_region_values(
        grid=game_state.our_ship_locations,
        top_row_idx=ship1_row_idx,
        left_col_idx=ship1_col_idx,
        height=ship1_height,
        width=ship1_width,
        region_value=ship1_value,
        other_value=SHIP_LOCATION_EMPTY,
    )


    # this ship placement is invalid: collision with existing ship on square (8, 5)
    assert not game_state.place_ship(
        8,
        5,
        ship2_width,
        ship2_height,
        ship2_value,
        is_our_ship=True,
    )

    # check that only the original ship's squares are set
    _check_rectangular_region_values(
        grid=game_state.our_ship_locations,
        top_row_idx=ship1_row_idx,
        left_col_idx=ship1_col_idx,
        height=ship1_height,
        width=ship1_width,
        region_value=ship1_value,
        other_value=SHIP_LOCATION_EMPTY,
    )


def test_ship_invalid_dimensions():
    # placing a ship that has either dimension set to 0 should throw an AssertionError
    game_state = BattleshipGameState()

    ship1_row_idx, ship1_col_idx = 4, 5
    ship1_height, ship1_width = 5, 0
    ship1_value = 1

    ship2_row_idx, ship2_col_idx = 3, 6
    ship2_height, ship2_width = 0, 4
    ship2_value = 2

    ship3_row_idx, ship3_col_idx = 0, 3
    ship3_height, ship3_width = 0, 0
    ship3_value = 3

    with pytest.raises(AssertionError) as e_info:
        game_state.place_ship(
            ship1_row_idx,
            ship1_col_idx,
            ship1_width,
            ship1_height,
            ship1_value,
            is_our_ship=True,
        )

    with pytest.raises(AssertionError) as e_info:
        game_state.place_ship(
            ship2_row_idx,
            ship2_col_idx,
            ship2_width,
            ship2_height,
            ship2_value,
            is_our_ship=True,
        )

    with pytest.raises(AssertionError) as e_info:
        game_state.place_ship(
            ship3_row_idx,
            ship3_col_idx,
            ship3_width,
            ship3_height,
            ship3_value,
            is_our_ship=True,
        )
    
    _check_all_grid_squares_equal(game_state.our_ship_locations, SHIP_LOCATION_EMPTY)
