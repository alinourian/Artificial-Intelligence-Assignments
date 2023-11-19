import numpy as np
from board import Board
from player import Player


n = 8


def get_value(board, player_number):
    return np.sum(board == player_number) - np.sum(np.logical_and(board != player_number, board != -1))


class AlphaBetaPlayer(Player):
    def max_val(self, a, b, remaining_depth=0):
        if remaining_depth == 0:
            # print(self.board.imaginary_board_grid)
            return get_value(self.board.imaginary_board_grid, self.player_number)
        v = -float("inf")
        for i in range(n):
            for j in range(n):
                if self.board.is_imaginary_move_valid(self.player_number, i, j):
                    last_board = np.copy(self.board.imaginary_board_grid)
                    self.board.imagine_placing_piece(self.player_number, i, j)
                    v = max(v, self.min_val(a, b, remaining_depth=remaining_depth - 1))
                    self.board.imaginary_board_grid = last_board
                    if v >= b:
                        return v
                    a = max(a, v)
        return v

    def min_val(self, a, b, remaining_depth=0):
        if remaining_depth == 0:
            # print(self.board.imaginary_board_grid)
            return get_value(self.board.imaginary_board_grid, self.player_number)
        v = float("inf")
        for i in range(n):
            for j in range(n):
                if self.board.is_imaginary_move_valid(self.opponent_number, i, j):
                    last_board = np.copy(self.board.imaginary_board_grid)
                    self.board.imagine_placing_piece(self.opponent_number, i, j)
                    v = min(v, self.max_val(a, b, remaining_depth=remaining_depth - 1))
                    self.board.imaginary_board_grid = last_board
                    if v <= a:
                        return v
                    b = min(b, v)
        return v

    def get_next_move(self):
        b = self.board.get_board_grid()
        # print(b)
        self.board.start_imagination()
        for i in range(n):
            for j in range(n):
                b[i][j] = self.board.is_imaginary_move_valid(self.player_number, i, j)
        # print(b)
        depth = 5
        res_coordinates = None
        a = -float("inf")
        b = float("inf")
        res_val = self.max_val(a, b, depth)
        # print(res_val)
        # print(self.board.imaginary_board_grid)
        for i in range(n):
            for j in range(n):
                if self.board.is_imaginary_move_valid(self.player_number, i, j):
                    a = -float("inf")
                    b = float("inf")
                    last_board = np.copy(self.board.imaginary_board_grid)
                    self.board.imagine_placing_piece(self.player_number, i, j)
                    val = self.max_val(a, b, remaining_depth=depth)
                    # print(self.board.imaginary_board_grid)
                    self.board.imaginary_board_grid = last_board
                    # print(i, j, val, res_val)
                    if res_val <= val:
                        res_val = val
                        res_coordinates = (i, j)
        return res_coordinates