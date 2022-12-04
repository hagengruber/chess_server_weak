"""
    @Author: Schamberger Sandro:    22102471
    @Author: Hagengruber Florian:   22101608
    @Author: Joiko Christian:       22111097
"""
import socket
import multiprocessing as m
from multiprocessing import Queue
from multiprocessing import Lock
from model import Model
from queue import Empty


# controller queue nicht username uniwuq where name = userid
# get queue content nicht prarameter ändern
# registrierung controller 78 def registtration
# zuerst registrieren, dann login und dann spielen

class App:

    """Main function"""

    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.host = self.ip
        self.port = 8080
        self.threads = -1
        self.lobby = Queue()
        self.lobby.put({'lobby': [], 'games': []})

        self.game = Queue()
        self.game.put([])

        self.connect = Queue()
        self.connect.put(True)

        self.lock = Lock()

    @staticmethod
    def connect_and_run(conn, lobby, threads, lock):
        """Handles the Game for every User"""

        model = Model(conn, lobby, threads, lock)
        model.controller.model = model
        model.view.model = model
        model.view.clear_console()

        try:
            model.view.print_menu(False)
        finally:
            # If a User forces the disconnect (e.g. with an error) the mutex may be still locked
            try:
                lock.release()
            except ValueError:
                pass

    def run(self):
        """Handles connection requests"""

        m.Process(target=App.check_launch_lobby, args=(self.lock, self.lobby,)).start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print("Server is listening on " + str(self.ip) + " with Port " + str(self.port))
            s.listen()

            while True:

                while self.connect.qsize() != 0:
                    self.connect.get()
                    self.threads += 1
                    m.Process(target=App.listen, args=(s, self.connect, self.lobby, self.threads, self.lock)).start()

    @staticmethod
    def check_launch_lobby(lock, game):

        """Checks if two users a in the Lobby and creates a game room"""

        # built-in function because the function has to be static due to the pickle error
        def release_lock(lock_f):
            """Release the mutex"""

            try:
                lock_f.release()
            except ValueError:
                pass

        def write_queue_content(queue_f, content_f, lock_f, override=True, safe_mode=True):
            """Writes content in the queue"""

            # the mutex may be locked before the function call
            if safe_mode:
                lock_f.acquire()

            if override:
                while True:
                    try:
                        queue_f.get_nowait()
                    except Empty:
                        break
                old_content = []
            else:
                old_content = []
                while queue_f.qsize() != 0:
                    old_content.append(queue_f.get())

            old_content.append(content_f)

            for i in old_content:
                queue_f.put(i)

            if safe_mode:
                release_lock(lock_f)

        def get_queue_content(queue_f, lock_f, safe_mode=True):
            """Returns the content of the queue"""

            if safe_mode:
                lock_f.acquire()

            try:

                temp_f = queue_f.get_nowait()
                queue_f.put(temp_f)

                if safe_mode:
                    release_lock(lock_f)

                return temp_f

            except Empty:
                if safe_mode:
                    release_lock(lock_f)
                return None

        while True:

            # Origin Loop
            temp = get_queue_content(game, lock)

            if temp is None:
                continue

            if temp['lobby'] is None:
                continue

            lock.acquire()

            if len(temp['lobby']) >= 2:

                games = temp['games']
                lobby = temp['lobby']

                # Creates a Game Room
                games.append(
                    {'player1': temp['lobby'][0]['username'], 'player2': temp['lobby'][1]['username'],
                     'White': temp['lobby'][0]['username'], 'Black': temp['lobby'][1]['username'], 'last_move': None,
                     'currently_playing': temp['lobby'][0]['username'], 'remis': None})

                lobby.remove(lobby[0])
                lobby.remove(lobby[0])

                temp['lobby'] = lobby
                temp['games'] = games

                write_queue_content(game, temp, lock, override=True, safe_mode=False)

            release_lock(lock)

    @staticmethod
    def listen(s, connect, lobby, threads, lock):
        """Waits for a connection from a Client and starts the game loop"""
        conn, addr = s.accept()
        with conn:
            connect.put(True)
            print("Server is connected with port " + str(addr))
            welcome = "Hello. You are connected to the Chess Server. Your port is " + str(addr[1]) + '\n\n'
            conn.sendall(welcome.encode())

            m.Process(target=App.connect_and_run, args=(conn, lobby, threads, lock)).start()


if __name__ == "__main__":
    a = App()
    a.run()
