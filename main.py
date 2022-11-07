"""
    @Author: Schamberger Sandro:    22102471
    @Author: Hagengruber Florian:   22101608
"""
import socket
import multiprocessing as m
from model import Model


class app:

    def __init__(self):
        """looooooooooooooooooool"""
        self.ip = socket.gethostbyname(socket.gethostname())
        self.host = self.ip
        self.port = 8080

    @staticmethod
    def connect_and_run(conn):
        """Handles the Game for every User"""
        model = Model(conn)
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
                conn, addr = s.accept()
                with conn:
                    print("Server is connected with port " + str(addr))
                    welcome = "Hello. You are connected to the Chess Server. Your port is " + str(addr[1]) + '\n\n'
                    conn.sendall(welcome.encode())

                    m.Process(target=app.connect_and_run, args=(conn,)).start()


if __name__ == "__main__":
    a = app()
    a.run()
