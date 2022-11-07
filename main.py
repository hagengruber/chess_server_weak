"""
    @Author: Schamberger Sandro:    22102471
    @Author: Hagengruber Florian:   22101608
"""
import socket
from model import Model


class app:

    def __init__(self):

        self.host = 'localhost'
        self.port = 8080

    def run(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            print("Server is listening")
            s.listen()
            conn, addr = s.accept()
            with conn:
                print("Server is connected with port " + str(addr))
                welcome = "Hello. You are connected to the Chess Server. Your port is " + str(addr[1]) + '\n\n'
                conn.sendall(welcome.encode())

                while True:
                    # data = conn.recv(1024)
                    model = Model(conn)
                    model.controller.model = model
                    model.view.model = model
                    model.view.print_menu()


if __name__ == "__main__":

    a = app()
    a.run()
