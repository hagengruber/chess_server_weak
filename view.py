"""
    Module for displaying the current state of the game to the user
"""
import os
import pyfiglet as banner


class View:
    """Class that handles everything for the module"""

    def __init__(self, socket):
        self.socket = socket
        self.model = None
        self.last_board = None

    def update_board(self, state=""):
        """Updates the board to show recent movement"""
        self.clear_console()

        if state == "":
            state = self.model.board_state

        box_top = ' \u250C' + '\u2500\u2500\u2500\u252C' * 7 + '\u2500\u2500\u2500\u2510'
        box_middle = ' \u251C' + '\u2500\u2500\u2500\u253C' * 7 + '\u2500\u2500\u2500\u2524'
        box_bottom = ' \u2514' + '\u2500\u2500\u2500\u2534' * 7 + '\u2500\u2500\u2500\u2518'
        self.model.controller.print(self.model.currently_playing + ' is currently playing!\n')
        self.model.controller.print('   1   2   3   4   5   6   7   8\n')
        self.model.controller.print(box_top + '\n')
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i in range(8):
            row = letters[i]
            for j in range(8):
                if state[i * 8 + j] is not None:
                    if state[i * 8 + j] != self.last_board[i * 8 + j]:
                        row += '\u2502\x1b[6;30;42m' + ' ' + state[i * 8 + j].symbol + ' \x1b[0m'
                    else:
                        row += '\u2502' + ' ' + state[i * 8 + j].symbol + ' '
                else:
                    if state[i * 8 + j] != self.last_board[i * 8 + j]:
                        row += '\u2502\x1b[6;30;42m' + '   \x1b[0m'
                    else:
                        row += '\u2502' + '   '

            row += '\u2502'
            self.model.controller.print(row + '\n')
            if i != 7:
                self.model.controller.print(box_middle + '\n')
        self.model.controller.print(box_bottom + '\n')

        self.last_board = self.model.get_copy_board_state()

    def clear_console(self):
        """Clear the console of unnecessary stuff"""
        self.socket.sendall("\033[H\033[J".encode())

    def print_menu(self):
        """Display the starting menu and tell 'model' to ask the user what he wants to do"""

        message = banner.figlet_format("Chess Online")
        self.socket.sendall(message.encode())

        message = '\n\n-Enter a move by giving the coordinates of the starting point and the goal point\n'
        self.socket.sendall(message.encode())
        message = '-During a match you can enter "q" to quit, "s" to save or "m" to go back to the menu\n'
        self.socket.sendall(message.encode())
        message = '(1)PlayerVsPlayer   (2)PlayerVsBot   (3)LoadGame   (4)Exit\n'
        self.socket.sendall(message.encode())

        self.model.controller.get_menu_choice()
