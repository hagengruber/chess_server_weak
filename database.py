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

    def add_player(self, mail, password, username):
        """Adds a player to the 'Spieler' table"""
        self.open_connection()
        self.cur.execute("""INSERT INTO Spieler (mail, passwort, nutzername) VALUES
                            ('%s', '%s', '%s')""" % (mail, password, username))
        self.con.commit()
        self.close_connection()

    def add_game(self, player1_id, player2_id, victor_id):
        """Adds a completed game to the 'Spiele' table"""
        self.open_connection()
        self.cur.execute("""INSERT INTO Spiele (spieler1id, spieler2id, siegerid) VALUES 
                            ('%s', '%s', '%s')""" % (player1_id, player2_id, victor_id))
        self.con.commit()
        self.close_connection()

    def add_save(self, dataname):
        """Adds a savestate to the 'Speicherstände' table"""
        self.open_connection()
        self.cur.execute("""INSERT INTO Speicherstände (name) VALUES ('%s')""" % dataname)
        self.con.commit()
        self.close_connection()

    def add_win(self, player_id):
        """Increases the number of wins by one for a given player"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET siege = siege + 1 WHERE id = '%s'""" % player_id)
        self.con.commit()
        self.close_connection()

    def add_loss(self, player_id):
        """Increases the number of losses by one for a given player"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET niederlagen = niederlagen + 1 WHERE id = '%s'""" % player_id)
        self.con.commit()
        self.close_connection()

    def add_remis(self, player_id):
        """Increases the number of remis by one for a given player"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET remis = remis + 1 WHERE id = '%s'""" % player_id)
        self.con.commit()
        self.close_connection()

    def change_saveid(self, player_id, dataname):
        """Changes the saveid of a given player to the id of a given savestate"""
        self.open_connection()
        res = self.cur.execute("""SELECT id FROM Speicherstände WHERE name = '%s'""" % dataname)
        save_id = res.fetchone()[0]
        self.cur.execute("""UPDATE Spieler SET saveid = '%s' WHERE id = '%s'""" % (save_id, player_id))
        self.con.commit()
        self.close_connection()

    def change_elo(self, victor_id, loser_id, elo):
        """Changes the elo of a given player"""
        self.add_elo(victor_id, elo)
        self.remove_elo(loser_id, elo)

    def add_elo(self, player_id, elo):
        """Increase a players elo"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET elo = elo + '%s' WHERE id = '%s'""" % (elo, player_id))
        self.con.commit()
        self.close_connection()

    def remove_elo(self, player_id, elo):
        """Decrease a players elo"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET elo = elo - '%s' WHERE id = '%s'""" % (elo, player_id))
        self.con.commit()
        self.close_connection()

    def fetch_public_userdata(self, player_id):
        """Returns a players public data"""
        self.open_connection()
        res = self.cur.execute("""SELECT nutzername, siege, niederlagen, remis, elo 
                                  FROM Spieler WHERE id = '%s'""" % player_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_userdata(self, player_id):
        """Returns a players full data"""
        self.open_connection()
        res = self.cur.execute("""SELECT * FROM Spieler WHERE id = '%s'""" % player_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_public_gamedata(self, game_id):
        """Returns public information for a game"""
        self.open_connection()
        res = self.cur.execute("""SELECT spieler1id, spieler2id, siegerid FROM Spiele WHERE id = '%s'""" % game_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_gamedata(self, game_id):
        """Returns full information for a game"""
        self.open_connection()
        res = self.cur.execute("""SELECT * FROM Spiele WHERE id = '%s'""" % game_id)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_savedata(self, save_id):
        """Returns full information for a savestate"""
        self.open_connection()
        res = self.cur.execute("""SELECT * FROM Speicherstände WHERE id = '%s'""" % save_id)
        data = res.fetchall()
        self.close_connection()
        return data
