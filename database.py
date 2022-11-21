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

    def add_game(self, player1id, player2id, victorid):
        """Adds a completed game to the 'Spiele' table"""
        self.open_connection()
        self.cur.execute("""INSERT INTO Spiele (spieler1id, spieler2id, siegerid) VALUES 
                            ('%s', '%s', '%s')""" % (player1id, player2id, victorid))
        self.con.commit()
        self.close_connection()

    def add_save(self, dataname):
        """Adds a savestate to the 'Speicherstände' table"""
        self.open_connection()
        self.cur.execute("""INSERT INTO Speicherstände (name) VALUES ('%s')""" % dataname)
        self.con.commit()
        self.close_connection()

    def add_win(self, playerid):
        """Increases the number of wins by one for a given player"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET siege = siege + 1 WHERE id = '%s'""" % playerid)
        self.con.commit()
        self.close_connection()

    def add_loss(self, playerid):
        """Increases the number of losses by one for a given player"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET niederlagen = niederlagen + 1 WHERE id = '%s'""" % playerid)
        self.con.commit()
        self.close_connection()

    def add_remis(self, playerid):
        """Increases the number of remis by one for a given player"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET remis = remis + 1 WHERE id = '%s'""" % playerid)
        self.con.commit()
        self.close_connection()

    def change_saveid(self, playerid, dataname):
        """Changes the saveid of a given player to the id of a given savestate"""
        self.open_connection()
        res = self.cur.execute("""SELECT id FROM Speicherstände WHERE name = '%s'""" % dataname)
        saveid = res.fetchone()[0]
        self.cur.execute("""UPDATE Spieler SET saveid = '%s' WHERE id = '%s'""" % (saveid, playerid))

    def change_elo(self, playerid, elo):
        """Changes the elo of a given player"""
        self.open_connection()
        self.cur.execute("""UPDATE Spieler SET elo = '%s' WHERE id = '%s'""" % (elo, playerid))
        self.con.commit()
        self.close_connection()

    def fetch_public_userdata(self, playerid):
        """Returns a players public data"""
        self.open_connection()
        res = self.cur.execute("""SELECT nutzername, siege, niederlagen, remis, elo 
                                  FROM Spieler WHERE id = '%s'""" % playerid)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_userdata(self, playerid):
        """Returns a players full data"""
        self.open_connection()
        res = self.cur.execute("""SELECT * FROM Spieler WHERE id = '%s'""" % playerid)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_public_gamedata(self, gameid):
        """Returns public information for a game"""
        self.open_connection()
        res = self.cur.execute("""SELECT spieler1id, spieler2id, siegerid FROM Spiele WHERE id = '%s'""" % gameid)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_private_gamedata(self, gameid):
        """Returns full information for a game"""
        self.open_connection()
        res = self.cur.execute("""SELECT * FROM Spiele WHERE id = '%s'""" % gameid)
        data = res.fetchall()
        self.close_connection()
        return data

    def fetch_full_savedata(self, saveid):
        """Returns full information for a savestate"""
        self.open_connection()
        res = self.cur.execute("""SELECT * FROM Speicherstände WHERE id = '%s'""" % saveid)
        data = res.fetchall()
        self.close_connection()
        return data
