import pygame
import pygame_gui
from gui.grid import Grid
from game_state import BattleshipGameState


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

# TODO add labels for the home/tracking grid

# initialize game state
game_state = BattleshipGameState()

# TODO add a placement phase instead of hardcoding
our_ship1 = game_state.place_ship(
    top_row_idx=0,
    left_col_idx=0,
    ship_width=1,
    ship_height=3,
    ship_value=1,
    is_our_ship=True,
)
assert our_ship1
bad_ship1 = game_state.place_ship(
    top_row_idx=0,
    left_col_idx=1,
    ship_width=1,
    ship_height=3,
    ship_value=101,
    is_our_ship=True,
)
assert not bad_ship1
our_ship2 = game_state.place_ship(
    top_row_idx=0,
    left_col_idx=2,
    ship_width=1,
    ship_height=2,
    ship_value=2,
    is_our_ship=True,
)
assert our_ship2
bad_ship2 = game_state.place_ship(
    top_row_idx=3,
    left_col_idx=0,
    ship_width=3,
    ship_height=1,
    ship_value=102,
    is_our_ship=True,
)
assert not bad_ship2
our_ship3 = game_state.place_ship(
    top_row_idx=4,
    left_col_idx=0,
    ship_width=3,
    ship_height=1,
    ship_value=3,
    is_our_ship=True,
)
assert our_ship3

opponent_ship1 = game_state.place_ship(
    top_row_idx=0,
    left_col_idx=0,
    ship_width=1,
    ship_height=3,
    ship_value=1,
    is_our_ship=False,
)
assert opponent_ship1

# initialize the grids after placement phase
new_home_grid = game_state.get_player_home_grid()
new_tracking_grid = game_state.get_player_tracking_grid()
home_grid.update_board_text(new_home_grid)
tracking_grid.update_board_text(new_tracking_grid)

# disable grid based on which player's turn it is
if game_state.is_my_turn:
    home_grid.disable_board_buttons()
    tracking_grid.enable_board_buttons()
else:
    home_grid.enable_board_buttons()
    tracking_grid.disable_board_buttons()

clock = pygame.time.Clock()
is_running = True


while is_running:
    time_delta = clock.tick(30) / 1000.0

    # if game_state.is_game_over():
    #     home_grid.disable_board_buttons()
    #     tracking_grid.disable_board_buttons()
    # elif game_state.is_my_turn:
    #     home_grid.disable_board_buttons()
    #     tracking_grid.enable_board_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
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

                if game_state.is_game_over:
                    home_grid.disable_board_buttons()
                    tracking_grid.disable_board_buttons()
                elif game_state.is_my_turn:
                    home_grid.disable_board_buttons()
                    tracking_grid.enable_board_buttons()
                else:
                    home_grid.enable_board_buttons()
                    tracking_grid.disable_board_buttons()

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()