"""
    Module that manages operations on the database
"""
import sqlite3


class Database:
    """Class that handles everything for the module"""

    def __init__(self):
        self.con = None
        self.cur = None
        self.statement = None

    def open_connection(self):
        """Creates a new connection and a cursor"""
        self.con = sqlite3.connect("Chess_Online_DB.db")
        self.cur = self.con.Cursor()

    def close_connection(self):
        """Closes the connection and saves changes"""
        self.con.close()

    def add_player(self, mail, password, username):
        """Adds a player to the 'Spieler' table"""
        self.open_connection()
        self.con.execute("""INSERT INTO Spieler (mail, passwort, nutzername) VALUES
                            ('%s', '%s', '%s')""" % (mail, password, username))
        self.con.commit()
        self.close_connection()

    def add_game(self, player1id, player2id, victorid):
        """Adds a completed game to the 'Spiele' table"""
        self.open_connection()
        self.con.execute("""INSERT INTO Spiele (spieler1id, spieler2id, siegerid) VALUES 
                            ('%s', '%s', '%s')""" % (player1id, player2id, victorid))
        self.con.commit()
        self.close_connection()

    def add_save(self, dataname):
        """Adds a savestate to the 'Speicherstände' table"""
        self.open_connection()
        self.con.execute("""INSERT INTO Speicherstände (name) VALUES ('%s')""" % dataname)
        self.con.commit()
        self.close_connection()
