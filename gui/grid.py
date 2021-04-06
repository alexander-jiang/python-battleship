import pygame
import pygame_gui
from tabulate import tabulate

from typing import List, Optional, Tuple


class Grid:
    def __init__(
        self,
        ui_manager,
        board_left: int,
        board_top: int,
        square_w: int,
        square_h: int,
        num_rows: int,
        num_cols: int,
        initial_text: str = "",
    ):
        self._ui_manager = ui_manager
        self.num_rows = num_rows
        self.num_cols = num_cols

        board_buttons = []
        for row_idx in range(num_rows):
            row_buttons = []
            for col_idx in range(num_cols):
                row_buttons.append(
                    pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect(
                            (
                                board_left + col_idx * square_w,
                                board_top + row_idx * square_h,
                            ),
                            (square_w, square_h),
                        ),
                        text=initial_text,
                        manager=ui_manager,
                    )
                )
            board_buttons.append(row_buttons)
        self._board_buttons = board_buttons

    def get_board_buttons(self):
        return self._board_buttons

    def is_element_on_board(self, ui_element) -> bool:
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if ui_element == self._board_buttons[r][c]:
                    return True
        return False

    def get_element_index(self, ui_element) -> Optional[Tuple[int, int]]:
        for r in range(self.num_rows):
            for c in range(self.num_cols):
                if ui_element == self._board_buttons[r][c]:
                    return (r, c)
        return None

    def update_button_text(self, row_idx: int, col_idx: int, new_text: str):
        # TODO check indexes are in bounds
        self._board_buttons[row_idx][col_idx].set_text(new_text)

    def disable_board_buttons(self):
        for r in range(len(self._board_buttons)):
            for c in range(len(self._board_buttons[r])):
                self._board_buttons[r][c].disable()

    def enable_board_buttons(self):
        for r in range(len(self._board_buttons)):
            for c in range(len(self._board_buttons[r])):
                self._board_buttons[r][c].enable()

    def reset_board_ui(self, initial_text: str = ""):
        for r in range(len(self._board_buttons)):
            for c in range(len(self._board_buttons[r])):
                self._board_buttons[r][c].rebuild()
                self._board_buttons[r][c].set_text(initial_text)

    def update_board_text(self, text_list: List[List[Optional[str]]]):
        # print("updating board ui:")
        # print(tabulate(text_list, tablefmt="grid"))
        for r in range(len(self._board_buttons)):
            for c in range(len(self._board_buttons[r])):
                self._board_buttons[r][c].rebuild()
                if text_list[r][c] is None:
                    button_text = ""
                else:
                    button_text = text_list[r][c]
                self._board_buttons[r][c].set_text(button_text)
