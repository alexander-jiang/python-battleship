import pygame
import pygame_gui
import random
from gui.grid import Grid
from game_state import (
    BattleshipGameState,
    STANDARD_SHIP_DIMENSIONS,
    SHIP_LOCATION_EMPTY,
)
from ship_placement import random_ships_placement


display_w = 800
display_h = 500


home_grid_top = display_h // 2 - 150
home_grid_left = display_w // 2 - 350
home_grid_bottom = display_h // 2 + 150
home_grid_right = display_w // 2 - 50

tracking_grid_top = display_h // 2 - 150
tracking_grid_left = display_w // 2 + 50
tracking_grid_bottom = display_h // 2 + 150
tracking_grid_right = display_w // 2 + 350

num_rows = 10
num_cols = 10

square_w, square_h = (
    (home_grid_right - home_grid_left) // num_cols,
    (home_grid_bottom - home_grid_top) // num_rows,
)


pygame.init()

pygame.display.set_caption("Battleship")
window_surface = pygame.display.set_mode((display_w, display_h))

background = pygame.Surface((display_w, display_h))
background.fill(pygame.Color("#FFFFFF"))

manager = pygame_gui.UIManager((display_w, display_h), "data/themes/game_theme.json")


home_grid = Grid(
    manager,
    board_left=home_grid_left,
    board_top=home_grid_top,
    square_w=square_w,
    square_h=square_h,
    num_rows=num_rows,
    num_cols=num_cols,
    initial_text="",
)
tracking_grid = Grid(
    manager,
    board_left=tracking_grid_left,
    board_top=tracking_grid_top,
    square_w=square_w,
    square_h=square_h,
    num_rows=num_rows,
    num_cols=num_cols,
    initial_text="",
)

# add labels for the home/tracking grid
label_height = 50
home_grid_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        (
            home_grid_left,
            home_grid_top - label_height,
        ),
        (home_grid_right - home_grid_left, label_height),
    ),
    text="Home Grid",
    manager=manager,
)
tracking_grid_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        (
            tracking_grid_left,
            tracking_grid_top - label_height,
        ),
        (tracking_grid_right - tracking_grid_left, label_height),
    ),
    text="Tracking Grid",
    manager=manager,
)
game_status_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect(
        (
            0,
            0,
        ),
        (display_w, label_height),
    ),
    text="",
    manager=manager,
)


# initialize game state
game_state = BattleshipGameState()

available_squares = []
for r in range(game_state.num_rows):
    row = []
    for c in range(game_state.num_cols):
        row.append(True)
    available_squares.append(row)
opponent_ship_placements = random_ships_placement(
    STANDARD_SHIP_DIMENSIONS,
    available_squares=available_squares,
    num_rows=game_state.num_rows,
    num_cols=game_state.num_cols,
    rotate_allowed=True,
)
for idx in range(len(opponent_ship_placements)):
    ship_placement = opponent_ship_placements[idx]
    top_row_idx, left_col_idx, ship_height, ship_width = ship_placement
    game_state.place_ship(
        top_row_idx=top_row_idx,
        left_col_idx=left_col_idx,
        ship_width=ship_width,
        ship_height=ship_height,
        ship_value=idx + 1,
        is_our_ship=False,
    )

# initialize the grids after placement phase
new_home_grid = game_state.get_player_home_grid()
new_tracking_grid = game_state.get_player_tracking_grid()
home_grid.update_board_text(new_home_grid)
tracking_grid.update_board_text(new_tracking_grid)

# disable grid based on which player's turn it is
if not game_state.ships_placed:
    game_status_label.set_text("Place your ships!")
    home_grid.enable_board_buttons()
    tracking_grid.disable_board_buttons()
elif game_state.is_my_turn:
    game_status_label.set_text("Your turn!")
    home_grid.disable_board_buttons()
    tracking_grid.enable_board_buttons()
else:
    game_status_label.set_text("Opponent's turn!")
    home_grid.disable_board_buttons()
    tracking_grid.disable_board_buttons()

clock = pygame.time.Clock()
is_running = True

ship_dimensions = STANDARD_SHIP_DIMENSIONS.copy()
next_ship_index = 0

# delay counter for computer's turn
thinking_delay = 0

while is_running:
    time_delta = clock.tick(30) / 1000.0

    # disable buttons based on whose turn it is
    # TODO why does the opposite grid's button theme/color change when a player scores a hit
    # (but the turn hasn't finished)
    if game_state.is_game_over:
        game_status_label.set_text("Game over!")
        home_grid.disable_board_buttons()
        tracking_grid.disable_board_buttons()
    elif not game_state.ships_placed:
        game_status_label.set_text("Place your ships!")
        home_grid.enable_board_buttons()
        tracking_grid.disable_board_buttons()
    elif game_state.is_my_turn:
        game_status_label.set_text("Your turn!")
        home_grid.disable_board_buttons()
        tracking_grid.enable_board_buttons()
    else:
        # disable buttons and allow computer to move
        game_status_label.set_text("Opponent's turn!")
        home_grid.disable_board_buttons()
        tracking_grid.disable_board_buttons()
        if thinking_delay <= 0:
            thinking_delay = 15

        thinking_delay -= 1
        if not game_state.is_my_turn and thinking_delay <= 0:
            row_idx = random.randrange(game_state.num_rows)
            col_idx = random.randrange(game_state.num_cols)
            print(f"computer guesses ({row_idx}, {col_idx})")

            game_state.call_square(row_idx, col_idx)
            new_home_grid = game_state.get_player_home_grid()
            new_tracking_grid = game_state.get_player_tracking_grid()
            home_grid.update_board_text(new_home_grid)
            tracking_grid.update_board_text(new_tracking_grid)
            thinking_delay = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.USEREVENT:
            if not game_state.ships_placed and home_grid.is_element_on_board(
                event.ui_element
            ):
                if event.user_type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
                    row_idx, col_idx = home_grid.get_element_index(event.ui_element)
                    for r in range(
                        row_idx,
                        min(
                            game_state.num_rows,
                            row_idx + ship_dimensions[next_ship_index][1],
                        ),
                    ):
                        for c in range(
                            col_idx,
                            min(
                                game_state.num_cols,
                                col_idx + ship_dimensions[next_ship_index][0],
                            ),
                        ):
                            ship_loc_value = game_state.our_ship_locations.read_grid(
                                r, c
                            )
                            if ship_loc_value == SHIP_LOCATION_EMPTY:
                                home_grid.update_button_text(r, c, new_text="")
                            else:
                                home_grid.update_button_text(
                                    r, c, new_text=str(ship_loc_value)
                                )
                if event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED:
                    row_idx, col_idx = home_grid.get_element_index(event.ui_element)
                    ship_loc_value = game_state.our_ship_locations.read_grid(
                        row_idx, col_idx
                    )

                    if ship_loc_value == SHIP_LOCATION_EMPTY:
                        for r in range(
                            row_idx,
                            min(
                                game_state.num_rows,
                                row_idx + ship_dimensions[next_ship_index][1],
                            ),
                        ):
                            for c in range(
                                col_idx,
                                min(
                                    game_state.num_cols,
                                    col_idx + ship_dimensions[next_ship_index][0],
                                ),
                            ):
                                home_grid.update_button_text(
                                    r, c, new_text=str(next_ship_index + 1)
                                )
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    row_idx, col_idx = home_grid.get_element_index(event.ui_element)
                    ship_loc_value = game_state.our_ship_locations.read_grid(
                        row_idx, col_idx
                    )
                    if ship_loc_value == SHIP_LOCATION_EMPTY:
                        ship_placement_success = game_state.place_ship(
                            row_idx,
                            col_idx,
                            ship_width=ship_dimensions[next_ship_index][0],
                            ship_height=ship_dimensions[next_ship_index][1],
                            ship_value=next_ship_index + 1,
                            is_our_ship=True,
                        )
                        if ship_placement_success:
                            next_ship_index = (next_ship_index + 1) % len(
                                ship_dimensions
                            )
                            new_home_grid = game_state.get_player_home_grid()
                            home_grid.update_board_text(new_home_grid)
                    else:
                        # rotate the ship
                        rotate_success = game_state.rotate_ship_placement(
                            game_state.our_ship_locations, ship_loc_value
                        )
                        if rotate_success:
                            new_home_grid = game_state.get_player_home_grid()
                            home_grid.update_board_text(new_home_grid)
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if tracking_grid.is_element_on_board(event.ui_element):
                    row_idx, col_idx = tracking_grid.get_element_index(event.ui_element)

                    if game_state.is_my_turn:
                        game_state.call_square(row_idx, col_idx)
                        new_home_grid = game_state.get_player_home_grid()
                        new_tracking_grid = game_state.get_player_tracking_grid()
                        home_grid.update_board_text(new_home_grid)
                        tracking_grid.update_board_text(new_tracking_grid)
                    else:
                        print(f"not the player's turn!")
                elif home_grid.is_element_on_board(event.ui_element):
                    row_idx, col_idx = home_grid.get_element_index(event.ui_element)

                    if not game_state.is_my_turn:
                        game_state.call_square(row_idx, col_idx)
                        new_home_grid = game_state.get_player_home_grid()
                        new_tracking_grid = game_state.get_player_tracking_grid()
                        home_grid.update_board_text(new_home_grid)
                        tracking_grid.update_board_text(new_tracking_grid)
                    else:
                        print(f"not the opponent's turn!")

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()