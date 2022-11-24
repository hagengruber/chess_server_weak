"""
    Module that contains the classes for all the pieces of chess
"""
from abc import ABCMeta, abstractmethod
import math


class Piece(metaclass=ABCMeta):
    """Base class for all the other classes"""

    def __init__(self):
        self.model = None
        self.symbol = None
        self.colour = None
        self.moved = False
        self.position = None

    @abstractmethod
    def check_legal_move(self, position):
        """Return True if move is legal, False else"""
        pass

    def check_occupied_friendly(self, position, state):
        """Returns true if a given position exists and is occupied by a friendly piece"""
        if position in range(64):
            if state[position] is not None:
                if state[position].colour == self.model.currently_playing:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def check_occupied_hostile(self, position, state):
        """Returns true if a given position exists and is occupied by a hostile piece"""
        if position in range(64):
            if state[position] is not None:
                if state[position].colour != self.model.currently_playing:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def check_occupied(self, position, state):
        """Returns true if a given position exists and is occupied"""
        if position in range(64):
            if self.check_occupied_hostile(position, state) or self.check_occupied_friendly(position, state):
                return True
            else:
                return False
        else:
            return False

    def check_linear(self, state):
        """Returns a list of all free spaces north, east, west and south of a given space"""
        allowed = []

        main_row = math.floor(self.position / 8)
        main_column = self.position - (main_row * 7) - main_row

        space_to_check = self.position - 8

        while space_to_check in range(64):
            if not self.check_occupied_friendly(space_to_check, state):
                if self.check_occupied_hostile(space_to_check, state):
                    allowed.append(space_to_check)
                    break
                else:
                    allowed.append(space_to_check)
                    space_to_check = space_to_check - 8
            else:
                break

        space_to_check = self.position + 8

        while space_to_check in range(64):
            if not self.check_occupied_friendly(space_to_check, state):
                if self.check_occupied_hostile(space_to_check, state):
                    allowed.append(space_to_check)
                    break
                else:
                    allowed.append(space_to_check)
                    space_to_check = space_to_check + 8
            else:
                break

        space_to_check = self.position - 1
        column = -1

        while space_to_check in range(64):

            if main_column == 0 or column == 0:
                break

            row = math.floor(space_to_check / 8)
            column = space_to_check - (row * 7) - row

            if not self.check_occupied_friendly(space_to_check, state):
                if self.check_occupied_hostile(space_to_check, state):
                    allowed.append(space_to_check)
                    break
                else:
                    allowed.append(space_to_check)
                    space_to_check = space_to_check - 1
            else:
                break

        space_to_check = self.position + 1

        column = -1

        while space_to_check in range(64):

            if main_column == 7 or column == 7:
                break

            row = math.floor(space_to_check / 8)
            column = space_to_check - (row * 7) - row

            if not self.check_occupied_friendly(space_to_check, state):
                if self.check_occupied_hostile(space_to_check, state):
                    allowed.append(space_to_check)
                    break
                else:
                    allowed.append(space_to_check)
                    space_to_check = space_to_check + 1
            else:
                break
        return allowed

    def check_diagonal(self, state):
        """Returns a list of all free spaces northeast, southeast, southwest and northwest of a given space"""
        allowed = []

        main_row = math.floor(self.position / 8)
        main_column = self.position - (main_row * 7) - main_row

        space_to_check = self.position - 9
        row = main_row
        column = main_column
        while space_to_check in range(64):

            old_row = row
            old_column = column
            row = math.floor(space_to_check / 8)
            column = space_to_check - (row * 7) - row

            if row < old_row and column < old_column:

                if not self.check_occupied_friendly(space_to_check, state):
                    if self.check_occupied_hostile(space_to_check, state):
                        allowed.append(space_to_check)
                        break
                    else:
                        allowed.append(space_to_check)
                        space_to_check = space_to_check - 9
                else:
                    break
            else:
                break

        row = main_row
        column = main_column
        space_to_check = self.position + 9
        while space_to_check in range(64):

            old_row = row
            old_column = column
            row = math.floor(space_to_check / 8)
            column = space_to_check - (row * 7) - row

            if row > old_row and column > old_column:

                if not self.check_occupied_friendly(space_to_check, state):
                    if self.check_occupied_hostile(space_to_check, state):
                        allowed.append(space_to_check)
                        break
                    else:
                        allowed.append(space_to_check)
                        space_to_check = space_to_check + 9
                else:
                    break
            else:
                break

        row = main_row
        column = main_column
        space_to_check = self.position - 7
        while space_to_check in range(64):

            old_row = row
            old_column = column
            row = math.floor(space_to_check / 8)
            column = space_to_check - (row * 7) - row

            if row < old_row and column > old_column:

                if not self.check_occupied_friendly(space_to_check, state):
                    if self.check_occupied_hostile(space_to_check, state):
                        allowed.append(space_to_check)
                        break
                    else:
                        allowed.append(space_to_check)
                        space_to_check = space_to_check - 7
                else:
                    break
            else:
                break

        row = main_row
        column = main_column
        space_to_check = self.position + 7
        while space_to_check in range(64):

            old_row = row
            old_column = column
            row = math.floor(space_to_check / 8)
            column = space_to_check - (row * 7) - row

            if row > old_row and column < old_column:

                if not self.check_occupied_friendly(space_to_check, state):
                    if self.check_occupied_hostile(space_to_check, state):
                        allowed.append(space_to_check)
                        break
                    else:
                        allowed.append(space_to_check)
                        space_to_check = space_to_check + 7
                else:
                    break
            else:
                break
        return allowed


class Rook(Piece):
    """Class for Rooks"""

    def __init__(self, colour, position, model):
        Piece.__init__(self)
        self.model = model
        self.colour = colour
        self.symbol = self.set_symbol()
        self.position = position
        self.moved = False
        Rook.table = [
            [0, 0, 0, 5, 5, 0, 0, 0],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def set_symbol(self):
        """Returns the Symbol the given piece should display"""
        if self.model.show_symbols:
            if self.colour == 'White':
                return '\u265C'
            else:
                return '\u2656'
        else:
            if self.colour == 'White':
                return 'r'
            else:
                return 'R'

    def check_legal_move(self, position, state="", return_all=False):
        """Makes a list of all legal moves and returns True if the given position is part of them"""

        if state == "":
            state = self.model.board_state

        allowed = self.check_linear(state)

        if return_all:
            return allowed
        if position in allowed:
            return True
        else:
            return False


class Horse(Piece):
    """Class for Horses"""

    def __init__(self, colour, position, model):
        Piece.__init__(self)
        self.model = model
        self.colour = colour
        self.symbol = self.set_symbol()
        self.position = position
        Horse.table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 15, 20, 20, 15, 0, -30],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50]
        ]

    def set_symbol(self):
        """Returns the Symbol the given piece should display"""
        if self.model.show_symbols:
            if self.colour == 'White':
                return '\u265E'
            else:
                return '\u2658'
        else:
            if self.colour == 'White':
                return 'h'
            else:
                return 'H'

    def check_legal_move(self, position, state="", return_all=False):
        """Makes a list of all legal moves and returns True if the given position is part of them"""
        allowed = []

        if state == "":
            state = self.model.board_state

        row = math.floor(self.position / 8)
        column = self.position - (row * 7) - row

        if not self.check_occupied_friendly(self.position - 17, state) and row >= 2 and column >= 1:
            allowed.append(self.position - 17)
        if not self.check_occupied_friendly(self.position - 15, state) and row >= 2 and column <= 6:
            allowed.append(self.position - 15)
        if not self.check_occupied_friendly(self.position - 10, state) and row >= 1 and column >= 2:
            allowed.append(self.position - 10)
        if not self.check_occupied_friendly(self.position - 6, state) and row >= 1 and column <= 5:
            allowed.append(self.position - 6)
        if not self.check_occupied_friendly(self.position + 17, state) and row <= 5 and column <= 6:
            allowed.append(self.position + 17)
        if not self.check_occupied_friendly(self.position + 15, state) and row <= 5 and column >= 1:
            allowed.append(self.position + 15)
        if not self.check_occupied_friendly(self.position + 10, state) and row <= 6 and column <= 5:
            allowed.append(self.position + 10)
        if not self.check_occupied_friendly(self.position + 6, state) and row <= 6 and column >= 2:
            allowed.append(self.position + 6)
        if return_all:
            return allowed

        if position in allowed:
            return True
        else:
            return False


class Bishop(Piece):
    """Class for Bishops"""

    def __init__(self, colour, position, model):
        Piece.__init__(self)
        self.model = model
        self.colour = colour
        self.symbol = self.set_symbol()
        self.position = position
        Bishop.table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20]
        ]

    def set_symbol(self):
        """Returns the Symbol the given piece should display"""
        if self.model.show_symbols:
            if self.colour == 'White':
                return '\u265D'
            else:
                return '\u2657'
        else:
            if self.colour == 'White':
                return 'b'
            else:
                return 'B'

    def check_legal_move(self, position, state="", return_all=False):
        """Makes a list of all legal moves and returns True if the given position is part of them"""

        if state == "":
            state = self.model.board_state

        allowed = self.check_diagonal(state)

        if return_all:
            return allowed
        if position in allowed:
            return True
        else:
            return False


class Pawn(Piece):
    """Class for Pawns"""

    def __init__(self, colour, position, model):
        Piece.__init__(self)
        self.model = model
        self.colour = colour
        self.symbol = self.set_symbol()
        self.position = position
        self.moved = False
        Pawn.table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def set_symbol(self):
        """Returns the Symbol the given piece should display"""
        if self.model.show_symbols:
            if self.colour == 'White':
                return '\u265F'
            else:
                return '\u2659'
        else:
            if self.colour == 'White':
                return 'p'
            else:
                return 'P'

    def check_legal_move(self, position, state="", return_all=False):
        """Makes a list of all legal moves and returns True if the given position is part of them"""
        allowed = []
        if state == "":
            state = self.model.board_state

        row = math.floor(self.position / 8)
        column = self.position - (row * 7) - row

        if self.colour == 'White':
            if not self.check_occupied(self.position - 8, state):
                allowed.append(self.position - 8)
            if self.check_occupied_hostile(self.position - 9, state) and column != 0:
                allowed.append(self.position - 9)
            if self.check_occupied_hostile(self.position - 7, state) and column != 7:
                allowed.append(self.position - 7)
            if not self.moved:
                if not self.check_occupied(self.position - 16, state) and\
                        not self.check_occupied(self.position - 8, state):
                    allowed.append(self.position - 16)
        else:
            if not self.check_occupied(self.position + 8, state):
                allowed.append(self.position + 8)
            if self.check_occupied_hostile(self.position + 9, state) and column != 7:
                allowed.append(self.position + 9)
            if self.check_occupied_hostile(self.position + 7, state) and column != 0:
                allowed.append(self.position + 7)
            if not self.moved:
                if not self.check_occupied(self.position + 16, state) and\
                        not self.check_occupied(self.position + 8, state):
                    allowed.append(self.position + 16)

        if return_all:
            return allowed

        if position in allowed:
            return True
        else:
            return False

    def upgrade(self):
        """Returns True if the Pawn is in an upgrade-position"""
        if self.colour == 'Black':
            if self.position in range(56, 63):
                return True
            else:
                return False
        else:
            if self.position in range(0, 7):
                return True
            else:
                return False


class Queen(Piece):
    """Class for Queens"""

    def __init__(self, colour, position, model):
        Piece.__init__(self)
        self.model = model
        self.colour = colour
        self.symbol = self.set_symbol()
        self.position = position
        Queen.table = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20]
        ]

    def set_symbol(self):
        """Returns the Symbol the given piece should display"""
        if self.model.show_symbols:
            if self.colour == 'White':
                return '\u265B'
            else:
                return '\u2655'
        else:
            if self.colour == 'White':
                return 'q'
            else:
                return 'Q'

    def check_legal_move(self, position, state="", return_all=False):
        """Makes a list of all legal moves and returns True if the given position is part of them"""

        if state == "":
            state = self.model.board_state

        allowed = self.check_linear(state) + self.check_diagonal(state)
        if return_all:
            return allowed
        if position in allowed:
            return True
        else:
            return False


class King(Piece):
    """Class for Kings"""

    def __init__(self, colour, position, model):
        Piece.__init__(self)
        self.model = model
        self.colour = colour
        self.symbol = self.set_symbol()
        self.position = position
        self.moved = False

    def set_symbol(self):
        """Returns the Symbol the given piece should display"""
        if self.model.show_symbols:
            if self.colour == 'White':
                return '\u265A'
            else:
                return '\u2654'
        else:
            if self.colour == 'White':
                return 'k'
            else:
                return 'K'

    def check_legal_move(self, position, state="", return_all=False):
        """Makes a list of all legal moves and returns True if the given position is part of them"""
        allowed = []

        if state == "":
            state = self.model.board_state

        if not self.check_occupied_friendly(self.position - 9, state):
            allowed.append(self.position - 9)
        if not self.check_occupied_friendly(self.position - 8, state):
            allowed.append(self.position - 8)
        if not self.check_occupied_friendly(self.position - 7, state):
            allowed.append(self.position - 7)
        if not self.check_occupied_friendly(self.position - 1, state):
            allowed.append(self.position - 1)
        if not self.check_occupied_friendly(self.position + 1, state):
            allowed.append(self.position + 1)
        if not self.check_occupied_friendly(self.position + 7, state):
            allowed.append(self.position + 7)
        if not self.check_occupied_friendly(self.position + 8, state):
            allowed.append(self.position + 8)
        if not self.check_occupied_friendly(self.position + 9, state):
            allowed.append(self.position + 9)
        if return_all:
            return allowed
        if position in allowed:
            return True
        else:
            return False
