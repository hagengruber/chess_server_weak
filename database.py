"""
    Module that manages operations on the database
"""
import sqlite3


class Database:
    """Class that handles everything for the module"""

    def __init__(self):
        self.con = None
        self.cur = None

    def open_connection(self):
        """Creates a new connection and a cursor"""
        self.con = sqlite3.connect("Chess_Online_DB.db")
        self.cur = self.con.cursor()

    def close_connection(self):
        """Closes the connection and saves changes"""
        self.con.close()

    def add_player(self, mail, password, username, code):
        """Adds a player to the 'Spieler' table"""
        self.open_connection()
        self.cur.executescript("""INSERT INTO Spieler (mail, passwort, nutzername, aktivierungscode) VALUES
                            ('%s', '%s', '%s', '%s')""" % (mail, password, username, code))
        self.con.commit()
        self.close_connection()

    def add_game(self, player1_id, player2_id, victor_id):
        """Adds a completed game to the 'Spiele' table"""
        self.open_connection()
        self.cur.executescript("""INSERT INTO Spiele (spieler1id, spieler2id, siegerid) VALUES 
                            ('%s', '%s', '%s')""" % (player1_id, player2_id, victor_id))
        self.con.commit()
        self.close_connection()

    def add_save(self, dataname):
        """Adds a savestate to the 'Speicherstände' table"""
        self.open_connection()
        self.cur.executescript("""INSERT INTO Speicherstände (name) VALUES ('%s')""" % dataname)
        self.con.commit()
        pk = self.cur.lastrowid
        self.close_connection()
        return pk

    def remove_save(self, username):
        self.open_connection()

        res = self.cur.executescript("""SELECT saveid FROM Spieler WHERE id = '%s'""" % self.get_id(username))

        save_id = res.fetchall()[0][0]

        self.change_saveid(self.get_id(username), 0, end_connection=False)

        self.cur.executescript("""DELETE FROM Speicherstände WHERE id='%s'""" % save_id)
        self.con.commit()
        self.close_connection()

    def add_win(self, player_id):
        """Increases the number of wins by one for a given player"""
        self.open_connection()
        self.cur.executescript(
            """UPDATE Spieler SET siege = siege + 1 WHERE id = '%s'""" % player_id)
        self.con.commit()
        self.close_connection()

    def add_loss(self, player_id):
        """Increases the number of losses by one for a given player"""
        self.open_connection()
        self.cur.executescript(
            """UPDATE Spieler SET niederlagen = niederlagen + 1 WHERE id = '%s'""" % player_id)
        self.con.commit()
        self.close_connection()

    def add_remis(self, player_id):
        """Increases the number of remis by one for a given player"""
        self.open_connection()
        self.cur.executescript(
            """UPDATE Spieler SET remis = remis + 1 WHERE id = '%s'""" % player_id)
        self.con.commit()
        self.close_connection()

    def change_saveid(self, player_id, save_id, end_connection=True):
        """Changes the saveid of a given player to the id of a given savestate"""
        self.open_connection()
        self.cur.executescript("""UPDATE Spieler SET saveid = '%s' WHERE id = '%s'""" % (save_id, player_id))
        self.con.commit()
        if end_connection:
            self.close_connection()

    def change_elo(self, victor_id, loser_id, elo):
        """Changes the elo of a given player"""
        self.add_elo(victor_id, elo)
        self.remove_elo(loser_id, elo)

    def add_elo(self, player_id, elo):
        """Increase a players elo"""
        self.open_connection()
        self.cur.executescript(
            """UPDATE Spieler SET elo = elo + '%s' WHERE id = '%s'""" % (elo, player_id))
        self.con.commit()
        self.close_connection()

    def remove_elo(self, player_id, elo):
        """Decrease a players elo"""
        self.open_connection()
        self.cur.executescript(
            """UPDATE Spieler SET elo = elo - '%s' WHERE id = '%s'""" % (elo, player_id))
        self.con.commit()
        self.close_connection()

    def fetch_public_userdata(self, player_id):
        """Returns a players public data"""
        self.open_connection()
        res = self.cur.executescript("""SELECT nutzername, siege, niederlagen, remis, elo 
                                  FROM Spieler WHERE id = '%s'""" % player_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_userdata(self, player_id):
        """Returns a players full data"""
        self.open_connection()
        res = self.cur.executescript(
            """SELECT * FROM Spieler WHERE id = '%s'""" % player_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_public_gamedata(self, game_id):
        """Returns public information for a game"""
        self.open_connection()
        res = self.cur.executescript(
            """SELECT spieler1id, spieler2id, siegerid FROM Spiele WHERE id = '%s'""" % game_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_gamedata(self, game_id):
        """Returns full information for a game"""
        self.open_connection()
        res = self.cur.executescript(
            """SELECT * FROM Spiele WHERE id = '%s'""" % game_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_savedata(self, save_id):
        """Returns full information for a savestate"""
        self.open_connection()
        res = self.cur.executescript(
            """SELECT * FROM Speicherstände WHERE id = '%s'""" % save_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_general_data(self, filter, database, sql_exec=""):
        """Executes SQL statements for general purpose"""
        self.open_connection()
        res = self.cur.executescript("SELECT " + filter +
                               " FROM " + database + " " + sql_exec)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_general_data(self, filter, table, sql_exec=""):
        """Executes SQL statements for general select purpose"""
        self.open_connection()
        res = self.cur.executescript("SELECT " + filter +
                               " FROM " + table + " " + sql_exec)
        data = res.fetchall()
        self.close_connection()
        return data

    def get_id(self, username):
        """Gets the id from Username"""
        self.open_connection()
        res = self.cur.executescript("""SELECT id 
                                  FROM Spieler WHERE nutzername = '%s'""" % username)
        data = res.fetchall()
        self.close_connection()

        data = int(data[0][0])

        return data

    def update_general_data(self, table, column, content, sql_exec=""):
        """Executes SQL statements for general update purpose"""
        self.open_connection()
        self.cur.executescript("UPDATE " + table + " SET " + column + "=" + content + " " + sql_exec)
        self.con.commit()
        self.close_connection()

    def get_GameSave(self, username):

        self.open_connection()
        res = self.cur.executescript("""SELECT saveid FROM Spieler WHERE nutzername = '%s'""" % username)
        save_game = res.fetchall()[0][0]

        res = self.cur.executescript("""SELECT name FROM Speicherstände WHERE id = '%s'""" % save_game)

        data = res.fetchall()
        self.close_connection()

        try:
            data = data[0][0]
        except IndexError:
            return False

        return data
