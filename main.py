import argparse
import socket
import select
import sys
import threading
import re


def retrieveIP():
    ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    return ip


class Server:
    def __init__(self,port=55555):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}

        self.aliases = {}

        self.host = socket.gethostname()
        self.port = port

        self.s.bind((self.host, self.port))
        self.ip = retrieveIP()

        self.help = {"/help, /?": "display this help message",
                     "/pm [ip] [message]": "send a message only to certain ip",
                     "/file [ip] [filepath]": "send a file (coming soon)",
                     "/alias [ip] [alias]": "set a temporary alias for an IP address"}

    def clientthread(self, conn, addr):
        conn.send(b'Welcome to this chatroom!')
        while True:
            try:
                message = conn.recv(2048).decode()
                sender = addr[0]
                if sender in self.aliases:
                    sender = self.aliases[sender]
                if message:
                    if message.startswith("/"):
                        if re.match("^/help$",message):
                            message_to_send = "\n".join(['{:30} {}'.format(k,self.help[k]) for k in self.help])
                            print(sender,"requested help")
                            self.broadcast(message_to_send,conn,only=[addr[0]])
                        elif re.match("^/pm (.+?) (.+)",message):
                            match = re.match("^/pm (.+?) (.+)",message)
                            to = match.group(1)
                            message = match.group(2)
                            message_to_send = "{}->You>{}".format(sender,message)
                            print("{}->{}>{}".format(sender,to,message))
                            self.broadcast(message_to_send,conn,only=[to])
                        elif re.match("^/file (.+?) (.+)", message):
                            match = re.match("^/file (.+?) (.+)", message)
                            to = match.group(1)
                            fp = match.group(2)
                            self.sendfile(open(fp,"rb"), to)
                        elif re.match("^/alias (.+?) (.+)", message):
                            match = re.match("^/alias (.+?) (.+)", message)
                            ip = match.group(1)
                            alias = match.group(2)
                            self.aliases[ip] = alias
                    else:
                        message_to_send = "{}>{}".format(sender,message)
                        print(message_to_send)
                        self.broadcast(message_to_send, conn)

                else:
                    self.remove(conn)

            except:
                continue

    def sendfile(self,file,to):
        for c in self.clients:
            if self.clients[c] == to:
                c.sendfile(file)

    def broadcast(self, message, connection, only=()):
        for c in self.clients:
            if only:
                condition = self.clients[c] in only
            else:
                condition = c != connection
            if condition:
                try:
                    c.send(message.encode())
                except:
                    c.close()
                    del self.clients[c]

    def remove(self,connection):
        if connection in self.clients:
            del self.clients[connection]

    def start(self):
        self.s.listen(100)
        while True:
            conn, addr = self.s.accept()
            self.clients[conn] = addr[0]
            print(addr[0] + " connected.")
            threading.Thread(target=self.clientthread, args=(conn, addr)).start()

        conn.close()
        self.s.close()


class Client:
    def __init__(self, target, port=55555):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = socket.gethostname()
        self.target = target
        self.port = port

        self.s.connect((self.target, self.port))
        self.ip = retrieveIP()

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
                    if not message.startswith("/"):
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
        print("Chat initiated with IP {} on port {}".format(server.ip,server.port))
        server.start()
    else:
        client = Client(args.target,args.port)




