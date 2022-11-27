"""
    Module for getting and processing input from the user
"""

from algorithm import AI
import json
import sys
import os
import pathlib
from pieces import *
import database
import re
from mail import Mail


def get_files(i):
    """Get Files from Directory"""
    if i == 1:
        return pathlib.Path().absolute()
    else:
        dirPath = pathlib.Path().absolute()
        return [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]


class Controller:
    """Class that handles everything for the module"""

    def __init__(self, view, socket, games, num_of_thread, lock):
        self.socket = socket
        self.model = None
        self.view = view
        self.ai = None
        self.user_ai = None
        self.load_game = False
        self.games = games
        self.user = {'username': None, 'num_of_thread': num_of_thread, 'game_queue': None, 'color': '', 'enemy': ''}
        self.lock = lock
        self.db = database.Database()

    def logout(self):

        if self.user['username'] is None:
            self.view.print("You are already logged out\n")
            return
        else:
            self.user['username'] = None
            self.view.print("Logout successful\n")
            return

    def login(self):
        """user login"""

        if self.user['username'] is not None:
            self.view.print("You are already logged in as " + str(self.user['username']) + "\n")
            return

        mail = self.view.input("email address: ")
        password = self.view.input("password: ")

        res = self.db.fetch_general_data("*", "Spieler", "WHERE mail='" + mail + "' and passwort='" + password + "';")

        if len(res) == 0:
            self.view.print("Invalid credentials\n")
            return

        if res[0][9] is not None:
            code = self.view.input("Enter your activation Code: ")
            if code == res[0][9]:
                self.db.update_general_data('Spieler', '"aktivierungscode"', 'NULL', 'WHERE mail="' + mail + '";')
            else:
                self.view.print("Wrong activation Code\n")
                return

        self.user['username'] = res[0][3]
        self.view.print("Login successful\n")
        return

    def registration(self):
        """registers a User"""

        # Get the new email address and password
        res = "bla"
        mail = ""
        password = ""

        while len(res) != 0:

            mail = self.view.input("Enter your email address: ")

            try:

                if mail.split("@")[1] == "stud.th-deg.de" or mail.split("@")[1] == "th-deg.de":
                    valid_th_mail = True
                else:
                    valid_th_mail = False

            except IndexError:
                valid_th_mail = False

            if len(mail) == 0 or not valid_th_mail:
                self.view.print("Your input was not a valid email address\n")
                continue

            res = self.db.fetch_general_data("mail", "Spieler", "WHERE mail='" + mail + "';")

            if len(res) != 0:
                self.view.print("This email address is already taken\n")
                continue

        while len(password) == 0:

            password = self.view.input("Enter a new password: ")

            if len(password) == 0:
                self.view.print("Your input was not a valid password\n")
                continue

        # ToDo: Check username: for now: florian.hagengruber@stud.th-deg.de -> f.hagengruber
        username = mail.split(".")[0][0] + "." + mail.split(".")[1].split("@")[0]

        m = Mail()
        code = Mail.create_code()

        self.db.add_player(mail, password, username, code)

        m.send_mail(mail, code)

        self.view.print("User registration was successful\n")
        self.view.print("The activation Code for your account was send to your email address\n")

    def init_board(self, return_board=False):
        if not self.load_game:
            self.model.reset_pieces()
            # initializes the previous board of the view
            self.view.last_board = self.model.get_copy_board_state()
        else:
            for _ in range(64):
                if self.model.board_state[_] is not None:
                    self.model.pieces.append(self.model.board_state[_])

        if return_board:
            return self.model.board_state
        else:
            self.model.view.update_board()
            return None

    def start_game(self):

        """Starts the Game and goes into the Game Loop"""

        self.init_board()

        self.model.view.update_board()
        self.get_movement_choice(self.view.get_movement_choice())

        self.model.currently_playing = 'Black'

        if self.model.ai:
            self.user_ai.move()
            self.model.currently_playing = 'White'
            while self.model.check_for_king():
                if self.model.currently_playing == 'Black':
                    self.user_ai.move()
                else:
                    self.get_movement_choice(self.view.get_movement_choice())

                if self.model.currently_playing == 'White':
                    self.model.currently_playing = 'Black'
                else:
                    self.model.currently_playing = 'White'

        else:
            while self.model.check_for_king():
                self.get_movement_choice(self.view.get_movement_choice())
                if self.model.currently_playing == 'White':
                    self.model.currently_playing = 'Black'
                else:
                    self.model.currently_playing = 'White'

        self.view.print(self.model.currently_playing + ' lost because his king died!')

        self.get_after_game_choice(self.view.get_after_game_choice())

    def get_after_game_choice(self, input):
        """Asks the player if he wants to play another game"""

        if input.lower() == 'y' or input.lower() == 'yes':
            self.view.clear_console()
            self.start_game()
        elif input.lower() == 'n' or input.lower() == 'no':
            self.view.clear_console()
            self.view.print_menu()
        else:
            self.view.invalid_input('Please answer with "yes" or "no"')
            self.get_after_game_choice(self.view.get_after_game_choice())

    def join_lobby(self):
        self.view.print("Join Lobby...\n")

        self.lock.acquire()

        temp = self.get_queue_content(self.games, safe_mode=False)

        if temp is None:
            self.write_queue_content(self.games, {'lobby': [], 'games': []})
            temp = {'lobby': [], 'games': []}

        temp['lobby'].append(self.user)

        self.write_queue_content(self.games, temp, safe_mode=False)

        self.lock.release()

        while True:

            self.lock.acquire()

            temp = self.get_queue_content(self.games, safe_mode=False)
            join = False

            if temp is None:
                self.lock.release()
                continue

            games = temp['games']

            for i in games:
                if i['player1'] == self.user['username'] or i['player2'] == self.user['username']:
                    join = True
                    break

            self.lock.release()

            if join:
                self.view.print("Join successful\n")
                break

    def get_queue_content(self, queue, safe_mode=True, release_lock=True):

        if safe_mode:
            self.lock.acquire()

        status = queue.empty()

        if not status:
            temp = queue.get()
            queue.put(temp)

            if safe_mode and release_lock:
                self.lock.release()

            return temp

        if safe_mode and release_lock:
            self.lock.release()

        return None

    def write_queue_content(self, queue, content, override=True, safe_mode=True):

        if safe_mode:
            self.lock.acquire()

        if override:
            while not queue.empty():
                queue.get()
            old_content = []
        else:
            old_content = []
            while queue.qsize() != 0:
                old_content.append(queue.get())

        old_content.append(content)

        for i in old_content:
            queue.put(i)

        if queue.empty():
            print("QUEUE WURDE OHNE INHALT BESCHRIEBEN")

        if safe_mode:
            self.lock.release()

    def get_menu_choice(self, input):
        """Gets input from user and processes the input"""

        if int(input):
            if len(input) == 1:

                if input == '1':
                    self.join_lobby()
                    self.coop()

                elif input == '2':
                    self.model.ai = True
                    self.user_ai = AI(self.model, self.view,
                                      "Black", "White", self)
                    self.model.show_symbols = self.get_symbol_preference(
                        self.view.get_symbol_preference())

                    self.start_game()

                elif input == '3':
                    cont = self.load()
                    if cont:
                        # self.view.update_board()
                        self.start_game()

                elif input == '4':
                    self.login()
                    self.view.clear_console()
                    self.view.print("Login successful\n")
                    self.view.print_menu()
                    self.get_menu_choice(self.view.get_menu_choice())

                elif input == '5':
                    self.registration()
                    self.view.clear_console()
                    self.view.print("Code was successful sent\n")
                    self.view.print_menu()
                    self.get_menu_choice(self.view.get_menu_choice())

                elif input == '6':
                    self.model.view.clear_console()
                    sys.exit()

            else:
                self.view.invalid_input('Please try again!')
                self.get_menu_choice(self.view.get_menu_choice())
        else:
            self.view.invalid_input("Please insert a valid Number")
            self.get_menu_choice(self.view.get_menu_choice())
            self.get_menu_choice(self.view.get_symbol_preference())

    def get_symbol_preference(self, input):
        """Asks the user whether he wants to use symbols(True) or letters(False)"""

        if re.match('^y', input) or re.match('yes', input):
            return True

        elif re.match('^n', input) or re.match('no', input):
            return False

        else:
            self.view.invalid_input(
                'Please answer the question with "yes" or "no"')
            self.get_symbol_preference(self.view.get_symbol_preference())

    def get_movement_choice(self, move, update=True):
        """Gets input from user during a game and processes the input"""

        move = move.upper()
        if len(move) == 1:

            if move == "Q":
                self.model.view.clear_console()
                sys.exit()

            elif move == "S":
                self.save()
                self.view.clear_console()
                self.view.print_menu()
                return self.get_movement_choice(self.view.get_menu_choice())

            elif move == "M":
                self.view.clear_console()
                self.view.print_menu()

            else:
                self.view.invalid_input('Please try again!')
                return self.get_movement_choice(self.view.get_movement_choice())

        elif re.match('^[--]', move):
            if move[2:] == "STATS":
                self.view.print("Stats")
                # opponent Stats
                cgid = 1  # Wann wird eine Spiel ID erstellt?
                # wie erhalte ich die SPieler ID

                # change_saveid ? ? ?

                id = self.db.fetch_public_gamedata(cgid)
                # ToDo: Spieler-ID holen
                data = self.db.fetch_public_userdata()
                self.view.show_stats(data)

            if move[2:] == "Surrender":
                self.view.print("aufgeben")
                # aufgeben das gleich wie Quit?

            if move[2:] == "REMIS":
                self.view.print("aufgeben")
                """ 
                        wie wird das Remis an den andern übertragen?
                        Wie wird das Remisangebot vermerkt?
                        
                        """

            if move[2:] == "HELP":
                self.view.get_help()

        else:
            if re.match('^[A-H][0-8][A-H][0-8]', move):

                start_pos = move[:2]
                goal_pos = move[-2:]

                self.model.move_piece(
                    self.model.correlation[start_pos], self.model.correlation[goal_pos], update=update)
                return move
            else:
                self.view.invalid_input(' Please try again!')
                return self.get_movement_choice(self.view.get_movement_choice())

    def coop(self):

        self.init_board()
        temp = None

        while temp is None:
            temp = self.get_queue_content(self.games)

        games = temp['games']

        for i in games:
            if i['player1'] == self.user['username'] or i['player2'] == self.user['username']:
                if i['White'] == self.user['username']:
                    self.user['color'] = 'White'
                else:
                    self.user['color'] = 'Black'

                if i['player1'] == self.user['username']:
                    self.user['enemy'] = i['player2']
                else:
                    self.user['enemy'] = i['player1']

        self.model.currently_playing = 'White'

        print_wait = True

        while self.model.check_for_king():

            temp = None

            while temp is None:
                temp = self.get_queue_content(self.games)

            games = temp['games']

            for i in range(len(games)):
                if games[i]['player1'] == self.user['username'] or games[i]['player2'] == self.user['username']:
                    if games[i]['currently_playing'] == self.user['username']:

                        print("Queue: " + str(temp))

                        print_wait = True

                        if games[i]['last_move'] is not None:
                            if games[i]['White'] == self.user['username']:
                                self.model.currently_playing = 'Black'
                            else:
                                self.model.currently_playing = 'White'

                            self.get_movement_choice(move=games[i]['last_move'], update=False)

                        self.model.currently_playing = self.user['color']

                        self.view.update_board()

                        games[i]['last_move'] = self.get_movement_choice(self.view.get_movement_choice())
                        games[i]['currently_playing'] = self.user['enemy']

                        temp['games'] = games
                        self.write_queue_content(self.games, temp, safe_mode=True)
                    else:
                        if print_wait:
                            self.view.print("The other Player is thinking...")
                            print_wait = False

    # Board aktuellen spieler und ob KI spielt View Symbol
    def save(self):
        """Saves the current state to a JSON-File"""
        GameSave = {'currently_playing': str(self.model.currently_playing),
                    'show_symbols': self.model.show_symbols,
                    'board_state': {},
                    'Ai': False}

        if self.model.ai:
            GameSave.update({'Ai': True})

        json_dict = {}
        for i in range(64):
            if self.model.board_state[i] is not None:
                lol = self.model.board_state[i].__doc__.split(" ")
                json_dict.update({str(i): {'piece': lol[2],
                                           'colour': str(self.model.board_state[i].colour),
                                           'moved': self.model.board_state[i].moved,
                                           'position': self.model.board_state[i].position}})
            else:
                json_dict.update({str(i): {'piece': None,
                                           'symbol': None,
                                           'colour': None,
                                           'moved': None,
                                           'position': None}})

        GameSave['board_state'].update(json_dict)

        path = str(get_files(1))
        name = "\\GameSave.json"

        with open(path + name, "w") as json_file:
            json.dump(GameSave, json_file)

    def load(self):
        """Loads a savestate"""
        files = get_files(2)
        name = 'GameSave.json'  # ggf Namen ändern

        if name in files:  # Parameter eintragen fürs testen
            with open("GameSave.json", "r") as Data:  # Parameter eintragen fürs testen
                GameSave = json.load(Data)
                # den aktuellen spieler abfragen

                self.model.currently_playing = GameSave['currently_playing']
                self.model.show_symbols = GameSave['show_symbols']
                self.load_game = True
                self.user_ai = AI(self.model, self.view, "Black", "White", self)

                if 'Ai' in GameSave:
                    self.ai = True
                    self.model.ai = True

                for i in range(64):
                    # Moved wird nicht übernommen
                    if GameSave['board_state'][str(i)]['piece'] == 'None':
                        self.model.board_state[i] = None

                    else:
                        if GameSave['board_state'][str(i)]['piece'] == 'Rooks':
                            self.model.board_state[i] = Rook(GameSave['board_state'][str(i)]['colour'],
                                                             i, self.model)
                        if GameSave['board_state'][str(i)]['piece'] == 'Horses':
                            self.model.board_state[i] = Horse(GameSave['board_state'][str(i)]['colour'],
                                                              i, self.model)
                        if GameSave['board_state'][str(i)]['piece'] == 'Bishops':
                            self.model.board_state[i] = Bishop(GameSave['board_state'][str(i)]['colour'],
                                                               i, self.model)
                        if GameSave['board_state'][str(i)]['piece'] == 'Queens':
                            self.model.board_state[i] = Queen(GameSave['board_state'][str(i)]['colour'],
                                                              i, self.model)
                        if GameSave['board_state'][str(i)]['piece'] == 'Kings':
                            self.model.board_state[i] = King(GameSave['board_state'][str(i)]['colour'],
                                                             i, self.model)
                        if GameSave['board_state'][str(i)]['piece'] == 'Pawns':
                            self.model.board_state[i] = Pawn(GameSave['board_state'][str(i)]['colour'],
                                                             i, self.model)

        else:
            self.view.print("There's no Save File for your Game!\n")
            return False

        self.view.last_board = self.model.get_copy_board_state()
        return True
