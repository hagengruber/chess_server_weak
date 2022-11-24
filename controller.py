"""
    Module for getting and processing input from the user
"""

from unittest import case
from algorithm import AI
import json
import sys
import os
import pathlib
from pieces import *
import re


def get_files(i):
    """Get Files from Directory"""
    if i == 1:
        return pathlib.Path().absolute()
    else:
        dirPath = pathlib.Path().absolute()
        return [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]


class Controller:
    """Class that handles everything for the module"""

    def __init__(self, view, socket):
        self.socket = socket
        self.model = None
        self.view = view
        self.ai = None
        self.user_ai = None
        self.load_game = False

    def start_game(self):
        """Starts the Game and goes into the Game Loop"""

        if not self.load_game:
            self.model.reset_pieces()
            # initializes the previous board of the view
            self.view.last_board = self.model.get_copy_board_state()
        else:
            for _ in range(64):
                if self.model.board_state[_] is not None:
                    self.model.pieces.append(self.model.board_state[_])

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

        self.print(self.model.currently_playing +
                   ' lost because his king died!')

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

    def get_menu_choice(self, input):
        """Gets input from user and processes the input"""

        if int(input):
            if len(input) == 1:

                if input == '1':
                    self.model.ai = False
                    self.model.show_symbols = self.get_symbol_preference(
                        self.view.get_symbol_preference())
                    self.start_game()

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

    def get_movement_choice(self, input):
        """Gets input from user during a game and processes the input"""

        input = input.upper()
        if input == "Q":
            self.model.view.clear_console()
            sys.exit()

        if input == "S":
            self.save()
            self.view.clear_console()
            self.view.print_menu()
            self.get_movement_choice(self.view.get_menu_choice())

        if input == "M":
            self.view.clear_console()
            self.view.print_menu()

        if len(input) < 4:
            self.view.invalid_input('Please try again!')
            self.get_movement_choice(self.view.get_movement_choice())
        else:
            if re.match('[A-H][0-9][A-H][0-9]', input):
                print("Hello")

            if re.match('^[--]', input):
                print("Statistiken")
                #-stats status des gegners
                #--surrender aufgebenbeendet das spiel und stats aktualisieren
                #--remis EINIGEN auf Remis

            lines = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            columns = ['1', '2', '3', '4', '5', '6', '7', '8']
            start_pos = input[:2]
            goal_pos = input[-2:]
                        
            if start_pos[0] in lines and goal_pos[0] in lines and start_pos[1] in columns and goal_pos[1] in columns:
                self.model.move_piece(
                self.model.correlation[start_pos], self.model.correlation[goal_pos])
            else:
                self.view.invalid_input('Please try again!')
                self.get_movement_choice(self.view.get_movement_choice())

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
                self.user_ai = AI(self.model, self.view,
                                  "Black", "White", self)

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
            self.print("There's no Save File for your Game!\n")
            return False

        self.view.last_board = self.model.get_copy_board_state()
        return True
