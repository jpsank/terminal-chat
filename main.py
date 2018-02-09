import os
import argparse
import socket
import select
import sys
import threading


class Server:
    def __init__(self,port=55555):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = []

        self.host = socket.gethostname()
        self.port = port

        self.s.bind((self.host, self.port))
        self.ip = self.s.getsockname()[0]

        self.s.listen(100)
        while True:
            conn, addr = self.s.accept()
            self.clients.append(conn)
            print(addr[0] + " connected.")
            threading.Thread(target=self.clientthread, args=(conn, addr)).start()

        conn.close()
        self.s.close()

    def clientthread(self, conn, addr):
        conn.send(b'Welcome to this chatroom!')
        while True:
            try:
                message = conn.recv(2048).decode()
                if message:
                    message_to_send = "{}>{}".format(addr[0],message)
                    print(message_to_send)
                    self.broadcast(message_to_send, conn)

                else:
                    self.remove(conn)

            except:
                continue

    def broadcast(self, message, connection):
        for c in self.clients:
            if c != connection:
                try:
                    c.send(message.encode())
                except:
                    c.close()
                    self.remove(c)

    def remove(self,connection):
        if connection in self.clients:
            self.clients.remove(connection)


class Client:
    def __init__(self, target, port=55555):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = socket.gethostname()
        self.target = target
        self.port = port

        self.s.connect((self.target, self.port))
        self.ip = self.s.getsockname()[0]

        closed = False
        while not closed:
            sockets_list = [sys.stdin, self.s]

            read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

            for socks in read_sockets:
                if socks == self.s:
                    message = socks.recv(2048)
                    if message:
                        print(message.decode())
                    else:
                        print("Connection closed.")
                        closed = True
                        break
                else:
                    message = sys.stdin.readline()
                    self.s.send(message.encode())
                    sys.stdout.write("You>")
                    sys.stdout.write(message)
                    sys.stdout.flush()
        self.s.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='target IP to connect to', type=str, dest="target")
    parser.add_argument('-p', help='port to listen (default 55555)', type=int, default=55555, dest="port")
    parser.add_argument('-l', '--listen', nargs='?', help='listen to [host]:[port] for incoming connections',
                        default=False, const=True)
    args = parser.parse_args()

    if args.listen:
        server = Server(args.port)
        print("Chat initiated with IP {} on port {}".format(server.host,server.port))
        server.start()
    else:
        client = Client(args.target,args.port)




