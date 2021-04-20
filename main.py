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

board_width = 300
board_height = 300

home_grid_top = display_h // 2 - 150
home_grid_left = display_w // 2 - 350
home_grid_bottom = home_grid_top + board_height
home_grid_right = home_grid_left + board_width

tracking_grid_top = display_h // 2 - 150
tracking_grid_left = display_w // 2 + 50
tracking_grid_bottom = tracking_grid_top + board_height
tracking_grid_right = tracking_grid_left + board_width

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

# add buttons for placement
button_width = (board_width // 2) - 20
button_padding = 10
button_height = 30
confirm_placement_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        (
            home_grid_left + (board_width // 2) - button_width - button_padding,
            home_grid_bottom + button_padding,
        ),
        (button_width, button_height),
    ),
    text="Confirm",
    manager=manager,
)
# add buttons for placement
randomize_placement_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(
        (
            home_grid_left + (board_width // 2) + button_padding,
            home_grid_bottom + button_padding,
        ),
        (button_width, button_height),
    ),
    text="Randomize",
    manager=manager,
)

# initialize game state
game_state = BattleshipGameState()
game_state.randomize_ship_placements(
    ship_dims=STANDARD_SHIP_DIMENSIONS, our_ships=False
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
placing_ships = True
confirm_placement_button.disable()

# delay counter for computer's turn
thinking_delay = 0

while is_running:
    time_delta = clock.tick(30) / 1000.0

    if placing_ships:
        ship_placement_render = game_state.get_player_home_grid()

    # disable buttons based on whose turn it is
    # TODO why does the opposite grid's button theme/color change when a player scores a hit
    # (but the turn hasn't finished)
    if game_state.is_game_over:
        game_status_label.set_text("Game over!")
        home_grid.disable_board_buttons()
        tracking_grid.disable_board_buttons()
    elif placing_ships:
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

    if game_state.ships_placed and not confirm_placement_button.is_enabled:
        print("ships are ready, enabling the confirmation button")
        confirm_placement_button.enable()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.USEREVENT:
            if placing_ships:
                # in ship placement phase
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == confirm_placement_button:
                        assert game_state.ships_placed
                        # confirming ship placement
                        placing_ships = False
                        confirm_placement_button.disable()
                        confirm_placement_button.hide()
                        randomize_placement_button.disable()
                        randomize_placement_button.hide()
                    if event.ui_element == randomize_placement_button:
                        # TODO UI bug: how come the button press sometimes is not registered?
                        print("randomizing player ship locations")
                        game_state.clear_all_ship_placements(
                            game_state.our_ship_locations
                        )
                        game_state.randomize_ship_placements(
                            ship_dims=STANDARD_SHIP_DIMENSIONS, our_ships=True
                        )
                        new_home_grid = game_state.get_player_home_grid()
                        home_grid.update_board_text(new_home_grid)
                    if home_grid.is_element_on_board(event.ui_element):
                        row_idx, col_idx = home_grid.get_element_index(event.ui_element)
                        ship_loc_value = game_state.our_ship_locations.read_grid(
                            row_idx, col_idx
                        )
                        if ship_loc_value == SHIP_LOCATION_EMPTY:
                            ship_width, ship_height = ship_dimensions[next_ship_index]
                            print(
                                f"attempting to place ship dims ({ship_height}, {ship_width}) on ({row_idx}, {col_idx})"
                            )
                            ship_placement_success = game_state.place_ship(
                                row_idx,
                                col_idx,
                                ship_width=ship_width,
                                ship_height=ship_height,
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
                if event.user_type == pygame_gui.UI_BUTTON_ON_HOVERED:
                    if home_grid.is_element_on_board(event.ui_element):
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
                                    ship_placement_render[r][c] = str(
                                        next_ship_index + 1
                                    )

                            home_grid.update_board_text(ship_placement_render)
                        else:
                            ship_placement_render = game_state.get_player_home_grid()
                            home_grid.update_board_text(ship_placement_render)
            else:
                # in playing phase
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if tracking_grid.is_element_on_board(event.ui_element):
                        row_idx, col_idx = tracking_grid.get_element_index(
                            event.ui_element
                        )

                        if game_state.is_my_turn:
                            game_state.call_square(row_idx, col_idx)
                            new_home_grid = game_state.get_player_home_grid()
                            new_tracking_grid = game_state.get_player_tracking_grid()
                            home_grid.update_board_text(new_home_grid)
                            tracking_grid.update_board_text(new_tracking_grid)
                        else:
                            print(f"not the player's turn!")
                    # elif home_grid.is_element_on_board(event.ui_element):
                    #     row_idx, col_idx = home_grid.get_element_index(event.ui_element)

                    #     if not game_state.is_my_turn:
                    #         game_state.call_square(row_idx, col_idx)
                    #         new_home_grid = game_state.get_player_home_grid()
                    #         new_tracking_grid = game_state.get_player_tracking_grid()
                    #         home_grid.update_board_text(new_home_grid)
                    #         tracking_grid.update_board_text(new_tracking_grid)
                    #     else:
                    #         print(f"not the opponent's turn!")

        manager.process_events(event)

    home_grid_rect = pygame.Rect(
        (home_grid_left, home_grid_top), (board_width, board_height)
    )
    if placing_ships and not home_grid_rect.collidepoint(pygame.mouse.get_pos()):
        ship_placement_render = game_state.get_player_home_grid()
        home_grid.update_board_text(ship_placement_render)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()