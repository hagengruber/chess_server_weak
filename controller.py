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
from queue import Empty

# controller queue nicht username uniwuq where name = userid
# get queue content nicht prarameter ändern
# registrierung controller 78 def registtration
# zuerst registrieren, dann login und dann spielen


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
        self.is_logged_in = False

    def logout(self):
        """Handles the logout of the user"""

        if not self.is_logged_in:
            return "You are already logged out"
        else:
            self.user['username'] = None
            self.is_logged_in = False
            return "Logout successful"

    def login(self):
        """Handles the login of the user"""

        if self.is_logged_in:
            return "You are already logged in as " + str(self.user['username'])

        mail = self.view.input("email address: ")

        # ToDo: Remove
        if mail == '0':
            mail = 'florian.hagengruber@stud.th-deg.de'
            password = 'aPassword'
        elif mail == '1':
            mail = 'mail@stud.th-deg.de'
            password = 'aPassword'
        elif mail == '2':
            mail = 't@stud.th-deg.de'
            password = 'aPassword'
        elif mail == '3':
            mail = 'sec@stud.th-deg.de'
            password = 'aPassword'
        else:
            password = self.view.input("password: ")

        res = self.db.fetch_general_data("*", "Spieler", "WHERE mail='" + mail + "' and passwort='" + password + "';")

        if len(res) == 0:
            # ToDo: CWE 549
            return "Invalid credentials"

        if res[0][9] is not None:
            code = self.view.input("Enter your activation Code: ")
            if code == res[0][9]:
                self.db.update_general_data('Spieler', '"aktivierungscode"', 'NULL', 'WHERE mail="' + mail + '";')
            else:
                return "Wrong activation Code"

        self.user['username'] = res[0][3]
        self.is_logged_in = True

        return "Login successful"

    def registration(self):
        """Handles the registration of the user"""

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

        username = mail.split(".")[0][0] + "." + mail.split(".")[1].split("@")[0]

        m = Mail()
        code = Mail.create_code()

        erg = m.send_mail(mail, code)

        if erg is not None:
            self.view.print(erg)
            return erg

        self.db.add_player(mail, password, username, code)

        return None

    def init_board(self, return_board=False):
        """Initializes the game board"""

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

        self.view.print(self.model.currently_playing + ' lost because his king died!')

        self.get_after_game_choice(self.view.get_after_game_choice())

    def get_after_game_choice(self, user_input):
        """Asks the player if he wants to play another game"""

        if self.check_input(user_input) == 1:
            self.view.clear_console()
            self.start_game()
        elif self.check_input(user_input) == 0:
            self.view.clear_console()
            self.view.print_menu(self.is_logged_in)
        else:
            self.get_after_game_choice(self.view.get_after_game_choice())

    def join_lobby(self):
        """User joins the lobby and waits for an Enemy"""

        self.view.print("Join Lobby...\n")

        self.lock.acquire()

        temp = None

        while temp is None:
            temp = self.get_queue_content(self.games, safe_mode=False)

        temp['lobby'].append(self.user)

        self.write_queue_content(self.games, temp, safe_mode=False)

        self.release_lock()

        self.view.print("Looking for Enemies...")

        while True:
            # Waits for an Enemy
            self.lock.acquire()

            temp = self.get_queue_content(self.games, safe_mode=False)
            join = False

            if temp is None:
                self.release_lock()
                continue

            games = temp['games']

            for i in games:
                if i['player1'] == self.user['username'] or i['player2'] == self.user['username']:
                    # Enemy found
                    join = True
                    break

            self.release_lock()

            if join:
                self.view.print("Join successful\n")
                break

    def release_lock(self):
        """Releases the Mutex"""

        try:
            self.lock.release()
        except ValueError:
            pass

    def get_queue_content(self, queue, safe_mode=True):
        """Returns the content of the Queue"""

        if safe_mode:
            self.lock.acquire()

        try:

            temp = queue.get_nowait()
            queue.put(temp)

            if safe_mode:
                self.release_lock()

            return temp

        except Empty:
            if safe_mode:
                self.release_lock()
            return None

    def write_queue_content(self, queue, content, override=True, safe_mode=True):
        """Writes the content in the Queue"""

        if safe_mode:
            self.lock.acquire()

        if override:
            while True:
                # Removes the content in the Queue
                try:
                    queue.get_nowait()
                except Empty:
                    break

            old_content = []

        else:
            old_content = []
            while True:
                try:
                    old_content.append(queue.get_nowait())
                except Empty:
                    break

        old_content.append(content)

        for i in old_content:
            queue.put_nowait(i)

        if safe_mode:
            self.release_lock()

    def get_menu_choice(self, user_input):
        """Gets input from user and processes the input"""

        try:

            type(int(user_input)) == int

        except ValueError:

            self.view.invalid_input('Please try again!')
            self.get_menu_choice(self.view.get_menu_choice())
            return

        if int(user_input):
            if len(user_input) == 1:

                if self.is_logged_in:
                    if user_input == '4':
                        user_input = '6'
                    elif user_input == '5':
                        user_input = '7'
                else:
                    if user_input == '1':
                        user_input = '4'
                    elif user_input == '2':
                        user_input = '5'
                    elif user_input == '3':
                        user_input = '7'
                    else:
                        user_input = '-1'

                if user_input == '1':
                    # User vs User
                    if not self.is_logged_in:
                        self.view.clear_console()
                        self.view.print_menu(self.is_logged_in,
                                             sub_message="\nLogin is required to play games with other players\n\n")
                        self.get_menu_choice(self.view.get_menu_choice())
                    else:
                        self.join_lobby()
                        self.coop()

                elif user_input == '2':
                    self.model.ai = True
                    self.user_ai = AI(self.model, self.view,
                                      "Black", "White", self)
                    self.model.show_symbols = self.get_symbol_preference(
                        self.view.get_symbol_preference())

                    self.start_game()

                elif user_input == '3':
                    # load game
                    cont = self.load()
                    if cont:
                        # self.view.update_board()
                        self.start_game()

                elif user_input == '4':
                    # login
                    message = self.login()
                    self.view.clear_console()
                    self.view.print_menu(self.is_logged_in, sub_message="\n" + message + "\n\n")
                    self.get_menu_choice(self.view.get_menu_choice())

                elif user_input == '5':
                    # registration
                    erg = self.registration()
                    self.view.clear_console()
                    if erg is None:
                        self.view.print_menu(self.is_logged_in, sub_message="\nCode was sent to your email address\n\n")
                    else:
                        self.view.print_menu(self.is_logged_in, sub_message="\n" + erg + "\n\n")

                    self.get_menu_choice(self.view.get_menu_choice())

                elif user_input == '6':
                    # logout
                    message = self.logout()
                    self.view.clear_console()
                    self.view.print_menu(self.is_logged_in, sub_message="\n" + message + "\n\n")
                    self.get_menu_choice(self.view.get_menu_choice())

                elif user_input == '7':
                    # exit
                    self.model.view.clear_console()
                    sys.exit()

                else:
                    self.view.invalid_input("Please insert a number")

        else:
            self.view.invalid_input("Please insert a valid Number")
            self.get_menu_choice(self.view.get_menu_choice())
            self.get_menu_choice(self.view.get_symbol_preference())

    def get_symbol_preference(self, user_input):
        """Asks the user whether he wants to use symbols(True) or letters(False)"""

        if self.check_input(user_input) == 1:
            return True

        elif self.check_input(user_input) == 0:
            return False

        else:
            self.get_symbol_preference(self.view.get_symbol_preference())

    def get_movement_choice(self, move, update=True):
        """Gets input from user during a game and processes the input"""

        move = move.upper()

        if re.match('^--', move):
            if move[2:] == "STATS":
                #eid = self.user['enemy']
                pers = self.db.fetch_public_userdata(14) # eid where nutzername = enemy

                self.view.show_stats(pers)
                self.get_movement_choice(self.view.get_movement_choice())

            if move[2:] == "SAVE":
                # ToDo: Darf während pvp nicht möglich sein
                self.save()
                self.view.clear_console()
                self.view.print_menu()
                return self.get_movement_choice(self.view.get_menu_choice())

            elif move[2:] == "Surrender":
                self.model.view.clear_console()
                # ToDo: Surrender implementieren

            elif move[2:] == "DRAW":
                draw = self.ask_draw()
                if not draw:
                    self.view.print("Draw was rejected\n")
                    return None
                else:
                    self.db.add_remis(self.db.get_id(self.user['username']))
                    self.db.add_remis(self.db.get_id(self.user['enemy']))
                    self.db.add_game(self.db.get_id(self.user['username']), self.db.get_id(self.user['enemy']), None)

                    self.remove_game()

                    self.view.clear_console()
                    self.view.print_menu(True)
                    self.get_menu_choice(self.view.get_menu_choice())
                    sys.exit()

            elif move[2:] == "HELP":
                self.view.get_help()

            else:
                self.view.invalid_input(' Please try again!')
                return self.get_movement_choice(self.view.get_movement_choice())

        elif re.match('^[A-H][0-8][A-H][0-8]', move):

                start_pos = move[:2]
                goal_pos = move[-2:]

                return self.model.move_piece(
                    self.model.correlation[start_pos], self.model.correlation[goal_pos], move=move, update=update)
        else:
            self.view.invalid_input(' Please try again!')
            return self.get_movement_choice(self.view.get_movement_choice())

    def remove_game(self):

        self.lock.acquire()

        temp = None
        while temp is None:
            temp = self.get_queue_content(self.games, safe_mode=False)

        games = temp['games']

        for i in games:
            if i['player1'] == self.user['username'] or i['player2'] == self.user['username']:
                # if the correct game room was found set the self.user variables
                games.remove(i)

                temp['games'] = games

                self.write_queue_content(self.games, temp, safe_mode=False)

                self.lock.release()

                break

    def ask_draw(self):

        """Asks the opponent for Draw and returns the answer"""

        self.view.print("Ask the opponent for Draw...")

        temp = None
        self.lock.acquire()

        while temp is None:
            temp = self.get_queue_content(self.games, safe_mode=False)

        games = temp['games']

        for i in range(len(games)):
            if games[i]['player1'] == self.user['username'] or games[i]['player2'] == self.user['username']:
                # if the correct game room was found

                games[i]['remis'] = self.user['username']

                write_success = False
                temp['games'] = games

                while not write_success:
                    self.write_queue_content(self.games, temp, safe_mode=False)

                    temp = None

                    while temp is None:
                        temp = self.get_queue_content(self.games, safe_mode=False)

                    if temp['games'][i]['remis'] is not None:
                        write_success = True

                self.release_lock()
                break

        answer = self.user['username']

        while answer == self.user['username']:

            temp = None
            while temp is None:
                temp = self.get_queue_content(self.games)

            games = temp['games']

            for i in range(len(games)):
                if games[i]['player1'] == self.user['username'] or games[i]['player2'] == self.user['username']:
                    # if the correct game room was found

                    if games[i]['remis'] is None:
                        continue

                    answer = games[i]['remis']
                    continue

        self.release_lock()

        if not answer:
            self.lock.acquire()

            temp = None
            while temp is None:
                temp = self.get_queue_content(self.games, safe_mode=False)

            games = temp['games']

            for i in range(len(games)):
                if games[i]['player1'] == self.user['username'] or games[i]['player2'] == self.user['username']:
                    # if the correct game room was found

                    games[i]['remis'] = None

                    write_success = False
                    temp['games'] = games

                    while not write_success:
                        self.write_queue_content(self.games, temp, safe_mode=False)

                        temp = None

                        while temp is None:
                            temp = self.get_queue_content(self.games, safe_mode=False)

                        if temp['games'][i]['remis'] is None:
                            write_success = True

                        self.release_lock()

                    break

        return answer

    def coop(self):

        self.init_board()
        temp = None

        while temp is None:
            temp = self.get_queue_content(self.games)

        games = temp['games']

        for i in games:
            if i['player1'] == self.user['username'] or i['player2'] == self.user['username']:
                # if the correct game room was found set the self.user variables
                if i['White'] == self.user['username']:
                    self.user['color'] = 'White'
                else:
                    self.user['color'] = 'Black'

                # set the enemy in self.user
                if i['player1'] == self.user['username']:
                    self.user['enemy'] = i['player2']
                else:
                    self.user['enemy'] = i['player1']

        self.model.currently_playing = 'White'

        # if the variable print_wait is True, print (below) "The other player is thinking"
        print_wait = True

        while self.model.check_for_king('White') and self.model.check_for_king('Black'):

            # Loop until the game is over
            temp = None

            while temp is None:
                temp = self.get_queue_content(self.games)

            games = temp['games']

            for i in range(len(games)):
                if games[i]['player1'] == self.user['username'] or games[i]['player2'] == self.user['username']:
                    # if the correct game room was found
                    if games[i]['currently_playing'] == self.user['username']:
                        # if the user can move a piece

                        print_wait = True

                        if games[i]['last_move'] is not None:
                            # if the other payer has moved a piece

                            if games[i]['White'] == self.user['username']:
                                self.model.currently_playing = 'Black'
                            else:
                                self.model.currently_playing = 'White'

                            # move the piece of the Enemy
                            self.get_movement_choice(move=games[i]['last_move'], update=False)

                        # Check if both kings are still alive
                        if not self.model.check_for_king('White') or not self.model.check_for_king('Black'):

                            self.view.clear_console()
                            self.view.print_menu(True)
                            self.get_menu_choice(self.view.get_menu_choice())
                            sys.exit()

                        self.model.currently_playing = self.user['color']

                        self.view.update_board()

                        last_move = None

                        while last_move is None:
                            # get the current move of the player and move the piece
                            last_move = self.get_movement_choice(self.view.get_movement_choice())

                        self.lock.acquire()

                        new_temp = None
                        while new_temp is None:
                            new_temp = self.get_queue_content(self.games, safe_mode=False)

                        games[i]['last_move'] = last_move
                        games[i]['currently_playing'] = self.user['enemy']

                        new_temp['games'][i] = games[i]

                        # update the queue with the game room
                        # since not all write operations does actually write, loop until the
                        # queue is successfully up-to-date
                        req = False
                        while not req:

                            q = None
                            while q is None:
                                q = self.get_queue_content(self.games, safe_mode=False)

                            try:

                                if q['games'][i]['currently_playing'] == self.user['enemy']:
                                    # if the write operation was successful
                                    req = True
                                else:
                                    # if the write operation failed
                                    self.write_queue_content(self.games, new_temp, safe_mode=False)

                            except IndexError:
                                self.write_queue_content(self.games, new_temp, safe_mode=False)

                        q = None
                        while q is None:
                            q = self.get_queue_content(self.games, safe_mode=False)

                        self.release_lock()

                    else:
                        if print_wait:
                            self.view.update_board()
                            self.view.print("The other Player is thinking...")
                            print_wait = False

                        draw = self.check_for_draw()

                        if not draw:
                            self.release_lock()
                        else:
                            self.view.clear_console()
                            self.view.print_menu(True)
                            self.get_menu_choice(self.view.get_menu_choice())
                            sys.exit()

                    break

        temp = None

        while temp is None:
            temp = self.get_queue_content(self.games)

        games = temp['games']

        for i in range(len(games)):
            if games[i]['player1'] == self.user['username'] or games[i]['player2'] == self.user['username']:
                # if the correct game room was found
                if games[i]['player1'] == self.user['username']:

                    if self.model.check_for_king('White'):
                        loser = games[i]['Black']
                        winner = games[i]['White']
                    else:
                        loser = games[i]['White']
                        winner = games[i]['Black']

                    self.db.add_win(self.db.get_id(winner))
                    self.db.add_loss(self.db.get_id(loser))

                    self.db.add_game(self.db.get_id(self.user['username']), self.db.get_id(self.user['enemy']),
                                     self.db.get_id(winner))

                    self.model.recalculate_elo(self.db.get_id(winner), self.db.get_id(loser))

                    self.remove_game()

                    self.view.clear_console()
                    self.view.print_menu(True)
                    self.get_menu_choice(self.view.get_menu_choice())
                    sys.exit()

                else:

                    self.view.clear_console()
                    self.view.print_menu(True)
                    self.get_menu_choice(self.view.get_menu_choice())
                    sys.exit()

    def check_for_draw(self):

        temp = None

        while temp is None:
            temp = self.get_queue_content(self.games)

        games, i = self.get_room(temp)

        if games[i]['remis'] is not None:
            answer = False

            while answer != 'y' and answer != 'n':

                games_new, a = self.get_room()
                if games_new[a]['remis'] is not None:
                    if not games_new[a]['remis']:
                        return False
                    elif games_new[a]['remis'] is True:
                        return True
                    else:
                        answer = self.view.input('\n' + str(games_new[a]['remis']) +
                                                 ' asks for Draw.\nAccept? (y/n)').lower()
                else:
                    return False

            if answer == 'y':
                answer = True
            else:
                answer = False

            self.lock.acquire()

            new_temp = None
            while new_temp is None:
                new_temp = self.get_queue_content(self.games, safe_mode=False)

            games[i]['remis'] = answer

            new_temp['games'][i] = games[i]

            while True:

                q = None
                while q is None:
                    q = self.get_queue_content(self.games, safe_mode=False)

                try:

                    if q['games'][i]['remis'] != self.user['enemy']:
                        # if the write operation was successful
                        self.release_lock()
                        return answer
                    else:
                        # if the write operation failed
                        self.write_queue_content(self.games, new_temp, safe_mode=False)

                except IndexError:
                    self.write_queue_content(self.games, new_temp, safe_mode=False)

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

    def check_input(self, input):

        input = input.upper()
        if re.match('^Y', input) or re.match('YES', input):
            return 1

        elif re.match('^N', input) or re.match('NO', input):
            return 0

        else:
            self.view.invalid_input(
                'Please answer the question with "yes" or "no"')

            return 2

    def get_room(self, temp=None):

        if temp is None:

            temp = None

            while temp is None:
                temp = self.get_queue_content(self.games)

        games = temp['games']

        for i in range(len(games)):
            if games[i]['player1'] == self.user['username'] or games[i]['player2'] == self.user['username']:
                return games, i
