"""
    Module for managing and manipulating data
"""
from view import View
from controller import Controller
from database import Database
from pieces import Rook, Horse, Bishop, Pawn, King, Queen


# noinspection PyTypeChecker
class Model:
    """Class that handles everything for the module"""

    def __init__(self, socket, lobby, num_of_thread, lock):

        self.board_state = list(None for _ in range(64))
        self.view = View(socket)
        self.controller = Controller(self.view, socket, lobby, num_of_thread, lock)
        self.database = Database()
        self.show_symbols = True
        self.correlation = {'A1': 0, 'A2': 1, 'A3': 2, 'A4': 3, 'A5': 4, 'A6': 5, 'A7': 6, 'A8': 7,
                            'B1': 8, 'B2': 9, 'B3': 10, 'B4': 11, 'B5': 12, 'B6': 13, 'B7': 14, 'B8': 15,
                            'C1': 16, 'C2': 17, 'C3': 18, 'C4': 19, 'C5': 20, 'C6': 21, 'C7': 22, 'C8': 23,
                            'D1': 24, 'D2': 25, 'D3': 26, 'D4': 27, 'D5': 28, 'D6': 29, 'D7': 30, 'D8': 31,
                            'E1': 32, 'E2': 33, 'E3': 34, 'E4': 35, 'E5': 36, 'E6': 37, 'E7': 38, 'E8': 39,
                            'F1': 40, 'F2': 41, 'F3': 42, 'F4': 43, 'F5': 44, 'F6': 45, 'F7': 46, 'F8': 47,
                            'G1': 48, 'G2': 49, 'G3': 50, 'G4': 51, 'G5': 52, 'G6': 53, 'G7': 54, 'G8': 55,
                            'H1': 56, 'H2': 57, 'H3': 58, 'H4': 59, 'H5': 60, 'H6': 61, 'H7': 62, 'H8': 63}
        self.pieces = []
        self.currently_playing = 'White'
        self.ai = None

    def reset_pieces(self):
        """Reset the board to its starting state"""
        model = self
        self.board_state[0] = Rook('Black', 0, model)
        self.board_state[1] = Horse('Black', 1, model)
        self.board_state[2] = Bishop('Black', 2, model)
        self.board_state[3] = Queen('Black', 3, model)
        self.board_state[4] = King('Black', 4, model)
        self.board_state[5] = Bishop('Black', 5, model)
        self.board_state[6] = Horse('Black', 6, model)
        self.board_state[7] = Rook('Black', 7, model)
        for i in range(8):
            self.board_state[8 + i] = Pawn('Black', 8 + i, model)
        for i in range(16, 56):
            self.board_state[i] = None
        self.board_state[56] = Rook('White', 56, model)
        self.board_state[57] = Horse('White', 57, model)
        self.board_state[58] = Bishop('White', 58, model)
        self.board_state[59] = Queen('White', 59, model)
        self.board_state[60] = King('White', 60, model)
        self.board_state[61] = Bishop('White', 61, model)
        self.board_state[62] = Horse('White', 62, model)
        self.board_state[63] = Rook('White', 63, model)
        for i in range(8):
            self.board_state[48 + i] = Pawn('White', 48 + i, model)
        self.pieces.clear()
        for _ in range(64):
            if self.board_state[_] is not None:
                self.pieces.append(self.board_state[_])

        self.check_rochade()

    def move_piece(self, start_pos, goal_pos, update=True):
        """Move a piece to a given position if the move is legal"""

        # Var "update": the AI trys different moves but the board shouldn't update while AI thinks

        model = self
        moved_piece = self.board_state[start_pos]
        killed_piece = self.board_state[goal_pos]

        if moved_piece is not None and moved_piece.colour == self.currently_playing:

            if self.board_state[start_pos].check_legal_move(goal_pos):
                self.board_state[goal_pos] = moved_piece
                self.board_state[start_pos] = None
                moved_piece.position = goal_pos
                if type(moved_piece) == Pawn:
                    if moved_piece.upgrade():
                        self.board_state[goal_pos] = Queen(
                            self.currently_playing, goal_pos, model)

                if type(moved_piece) == King and self.check_rochade:
                    if goal_pos == 62:
                        self.board_state[61] = self.board_state[63]
                        self.board_state[63] = None

                    if goal_pos == 58:
                        self.board_state[goal_pos + 1] = self.board_state[56]
                        self.board_state[56] = None

                    if goal_pos == 6:
                        self.board_state[6] = self.board_state[7]
                        self.board_state[0] = None

                    if goal_pos == 1 or goal_pos == 2:
                        self.board_state[goal_pos + 1] = self.board_state[0]
                        self.board_state[0] = None

                moved_piece.moved = True

                if killed_piece is not None:
                    self.pieces.remove(killed_piece)
                if update:
                    self.view.update_board()
                return True
            else:
                self.view.invalid_input('Sorry, this move is not legal. Please try again!')
                self.controller.get_movement_choice(self.view.get_movement_choice())
                return False

        else:
            self.view.invalid_input('There is no piece of your color on this space. Please try again!')
            self.controller.get_movement_choice(self.view.get_movement_choice())
            return False

    def check_for_king(self):
        """Check whether the king of the currently playing team is alive or not """
        king_alive = False
        for i in self.pieces:
            if type(i) == King and i.colour == self.currently_playing:
                king_alive = True
                break
        return king_alive

    def get_copy_board_state(self, state=None):
        """Deepcopy the board state"""

        if state is None:
            state = self.board_state

        temp = []

        for i in state:
            temp.append(i)

        return temp

    def check_rochade(self):
        """Returns True when Rochade is possible"""

        kopie = self.get_copy_board_state()

        if self.currently_playing == "White":
            row = kopie[56:]
        else:
            row = kopie[:8]

        if not row[0].moved and not row[4].moved and not row[7].moved:
            if row[1] is None and row[2] is None and row[3] is None or row[5] is None and row[6] is None:
                return True

    def recalculate_elo(self, victor_id, loser_id):
        victor_elo = self.database.fetch_general_data('elo', 'Spieler', 'WHERE id = ' + victor_id)
        loser_elo = self.database.fetch_general_data('elo', 'Spieler', 'WHERE id = ' + loser_id)
        elo_difference = max(victor_elo, loser_elo) - min(victor_elo, loser_elo)
        elo_difference = elo_difference / 400
        expected_value = 1 / (1 + 10**elo_difference)
        changed_elo = victor_elo + 20 * (1 - expected_value)
        elo_change = changed_elo - victor_elo
        self.database.add_elo(victor_id, elo_change)
        self.database.remove_elo(loser_id, elo_change)
