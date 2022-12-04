"""
    Module for displaying the current state of the game to the user
"""
import pyfiglet

# Formatierung von Ausgaben Leerzeichen oder Neue Zeile vorne oder hinten einheitlich?


class View:
    """Class that handles everything for the module"""

    def __init__(self, socket):
        self.socket = socket
        self.model = None
        self.last_board = None
        self.count = 1

    def input(self, text=None):
        if text is not None:
            self.print(text)
        return self.socket.recv(1024).decode().replace('\n', '')[:-1]

    def print(self, text):
        self.socket.sendall(text.encode())

    def update_board(self, state=""):
        self.count += 1
        """Updates the board to show recent movement"""
        self.clear_console()

        if state == "":
            state = self.model.board_state

        box_top = ' \u250C' + '\u2500\u2500\u2500\u252C' * 7 + '\u2500\u2500\u2500\u2510'
        box_middle = ' \u251C' + '\u2500\u2500\u2500\u253C' * 7 + '\u2500\u2500\u2500\u2524'
        box_bottom = ' \u2514' + '\u2500\u2500\u2500\u2534' * 7 + '\u2500\u2500\u2500\u2518'
        temp = self.model.controller.games
        
        games = self.model.controller.get_queue_content(temp)

        i = self.model.controller.loop_games(games)

        self.print(games[i]['currently_playing'] + ' is currently playing!\n')
        self.print('   1   2   3   4   5   6   7   8\n')
        self.print(box_top + '\n')
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i in range(8):
            row = letters[i]
            for j in range(8):
                if state[i * 8 + j] is not None:
                    if state[i * 8 + j] != self.last_board[i * 8 + j]:
                        row += '\u2502\x1b[6;30;42m' + ' ' + \
                            state[i * 8 + j].symbol + ' \x1b[0m'
                    else:
                        row += '\u2502' + ' ' + state[i * 8 + j].symbol + ' '
                else:
                    if state[i * 8 + j] != self.last_board[i * 8 + j]:
                        row += '\u2502\x1b[6;30;42m' + '   \x1b[0m'
                    else:
                        row += '\u2502' + '   '

            row += '\u2502'
            self.print(row + '\n')
            if i != 7:
                self.print(box_middle + '\n')
        self.print(box_bottom + '\n')

        self.last_board = self.model.get_copy_board_state()

    def clear_console(self):
        """Clear the console of unnecessary stuff"""
        self.socket.sendall("\033[H\033[J".encode())

    def print_menu(self, login, sub_message=None):
        """Display the starting menu and tell 'model' to ask the user what he wants to do"""

        message = pyfiglet.figlet_format("Chess Online")
        self.socket.sendall(message.encode())

        message = '\n\n-Enter a move by giving the coordinates of the starting point and the goal point\n'
        self.socket.sendall(message.encode())
        message = '-During a match you can either enter a legal Move or "--Help" for further commands\n'
        self.socket.sendall(message.encode())

        if login:
            message = '(1)PlayerVsPlayer   (2)PlayerVsBot   (3)LoadGame   (4)Logout   (5)Exit\n'
        else:
            message = '(1)Login   (2)Registration   (3)Exit\n'

        self.socket.sendall(message.encode())

        if sub_message is not None:
            self.socket.sendall(sub_message.encode())

        self.model.controller.get_menu_choice(self.get_menu_choice())

    def invalid_input(self, input):
        self.print('Invalid input! \n')
        self.print(input)

    def get_after_game_choice(self):
        self.print('Do you want to play another round? (Y/N): ')
        return input()

    def get_menu_choice(self):
        self.print('Please enter the number that corresponds to your desired menu: ')
        return self.input()

    def get_symbol_preference(self):
        self.print(
            'Do you want to use symbols? If not, letters will be used instead. (Y/N): ')
        return self.input()

    def get_movement_choice(self):
        self.print('Please enter your desired Move: ')
        return self.input()

    def show_stats(self, data):
        self.print('Stats of the opponent: '+str(data)+'\n')

    def get_help(self):
        self.print("legal move or\n")
        self.print("--stats - show opponent Stats\n")
        self.print("--save - Save and Quit Game\n")
        self.print("--remis - offer Remis\n")
        self.print("--surrender - Surrender\n")

    def accept_remis(self):
        self.print('Do you want to accept Remis? ')
        return self.input()

    def get_difficulty(self):
        self.print('How hard schould the AI be (1-5): ')
        return self.input()
