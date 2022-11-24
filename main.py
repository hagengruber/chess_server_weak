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


class App:

    def __init__(self):
        """looooooooooooooooooool"""
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
        model.view.print_menu()

    def run(self):
        """Handles connection requests"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print("Server is listening on " + str(self.ip) + " with Port " + str(self.port))
            s.listen()

            while True:

                while self.connect.qsize() != 0:
                    self.connect.get()
                    self.threads += 1
                    m.Process(target=App.listen, args=(s, self.connect, self.lobby, self.threads, self.lock)).start()

                self.check_launch_lobby()

    def get_queue_content(self, queue, safe_mode=True):
        if queue.qsize() > 0:

            if safe_mode:
                self.lock.acquire()

            temp = queue.get()
            queue.put(temp)

            if safe_mode:
                self.lock.release()

            return temp
        return None

    def write_queue_content(self, queue, content, override=True, safe_mode=True):

        if safe_mode:
            self.lock.acquire()

        if override:
            while queue.qsize() != 0:
                queue.get()
            old_content = []
        else:
            old_content = []
            while queue.qsize() != 0:
                old_content.append(queue.get())

        old_content.append(content)

        for i in old_content:
            queue.put(i)

        if safe_mode:
            self.lock.release()

    def check_launch_lobby(self):

        self.lock.acquire()

        temp = self.get_queue_content(self.lobby, safe_mode=False)

        if temp['lobby'] is None:
            return

        if len(temp['lobby']) >= 2:

            games = temp['games']
            lobby = temp['lobby']

            games.append(
                {'player1': temp['lobby'][0]['username'], 'player2': temp['lobby'][1]['username'],
                 'White': temp['lobby'][0]['username'], 'Black': temp['lobby'][1]['username'], 'last_move': None,
                 'currently_playing': temp['lobby'][0]['username']})

            lobby.remove(lobby[0])
            lobby.remove(lobby[0])

            temp['lobby'] = lobby
            temp['games'] = games

            self.write_queue_content(self.lobby, temp, override=True, safe_mode=False)
            print("Inhalt Lobby: " + str(self.get_queue_content(self.lobby, safe_mode=False)))

        self.lock.release()

    @staticmethod
    def listen(s, connect, lobby, threads, lock):
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
