import argparse
import socket
import select
import sys
import threading
import re
import os
import subprocess


re_ip = "(([0-9]+\.){3}[0-9]+)"


def retrieveIP():
    try:
        cmd = "ifconfig | grep -Eo 'inet (addr:)?{0}' | grep -Eo '{0}' | grep -v '127.0.0.1'".format(re_ip)
        ifconfig = os.popen(cmd).read()
        ips = ifconfig.split("\n")
        bcast = get_bcast_ip()
        ip_start = '.'.join(bcast.split('.')[:-1])
        ips = [i for i in ips if i.startswith(ip_start) and i != bcast]
        ip = ips[0]
    except:
        ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
    return ip


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class Server:
    def __init__(self,port=55555):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}

        self.aliases = {}

        self.host = socket.gethostname()
        self.port = port

        self.s.bind(("", self.port))
        self.ip = retrieveIP()

        self.help = {"/help, /?":          "display this help message",
                     "/pm [ip] [message]": "send a message only to certain ip",
                     "/file [filepath]":   "download a file from the server",
                     "/alias [alias]":     "set your name on this server (others will see this instead of your IP)",
                     "/members":           "return all members of this chat"}

    def clientthread(self, conn, addr):
        conn.send(b'Welcome to this chatroom!')
        while True:
            try:
                message = conn.recv(2048).decode()[:-1]
                sender = addr[0]
                if sender in self.aliases:
                    sender = self.aliases[sender]
                if message:
                    if message.startswith("/"):
                        if re.match("^/(help|\?)$",message):
                            message_to_send = "\n".join([' - {:30} {}'.format(k,self.help[k]) for k in self.help])
                            print(sender,"requested help")
                            self.broadcast(message_to_send,conn,only=[addr[0]])
                        elif re.match("^/pm (.+?) (.+)",message):
                            match = re.match("^/pm (.+?) (.+)",message)
                            toip = match.group(1)
                            if toip in self.aliases.values():
                                toip = {v: k for k,v in self.aliases.items()}[toip]
                            if toip in self.aliases:
                                toname = self.aliases[toip]
                            else:
                                toname = toip
                            if toip in self.clients.values():
                                message = match.group(2)
                                message_to_send = "{}->You>{}".format(sender,message)
                                print("{}->{}>{}".format(sender,toname,message))
                                self.broadcast(message_to_send,conn,only=[toip])
                            else:
                                print("{} tried to send a pm to '{}'".format(sender,toname))
                                self.broadcast("PM failed", conn, only=[addr[0]])
                        elif re.match("^/file (.+)", message):
                            match = re.match("^/file (.+)", message)
                            fp = match.group(1)
                            if os.path.isfile(fp):
                                file = open(fp,"rb")
                                self.sendfile(file, conn)
                                file.close()
                                print(sender, "retrieved a file '{}'".format(fp))
                            else:
                                print(sender, "tried to retrieve a nonexistent file '{}'".format(fp))
                                self.broadcast("File '{}' not found".format(fp), conn, only=[addr[0]])
                        elif re.match("^/alias (\S+)", message):
                            match = re.match("^/alias (\S+)", message)
                            alias = match.group(1)
                            print("{} set his/her alias to '{}'".format(sender, alias))
                            self.aliases[addr[0]] = alias
                        elif re.match("^/members$", message):
                            message_to_send = "\n".join([" - "+("{} ({})".format(a,self.aliases[a]) if a in self.aliases else a) for a in self.clients.values()])
                            print(sender, "requested member list")
                            self.broadcast(message_to_send, conn, only=[addr[0]])
                        else:
                            print("{} tried to execute unknown or incorrect usage of command '{}'".format(sender,message))
                            self.broadcast("Unknown or incorrect usage of command. Type '/help' for the list of commands", conn, only=[addr[0]])
                    else:
                        message_to_send = "{}>{}".format(sender,message)
                        print(message_to_send)
                        self.broadcast(message_to_send, conn)

                else:
                    if conn in self.clients:
                        message_to_send = sender + " disconnected."
                        print(message_to_send)
                        self.broadcast(message_to_send, conn)
                    self.remove(conn)

            except:
                continue

    def sendfile(self, file, connection):
        read = file.read(2048)
        while read:
            connection.send(read)
            read = file.read(2048)

    def broadcast(self, message, connection, only=()):
        remove = []
        for c in self.clients:
            if only:
                condition = self.clients[c] in only
            else:
                condition = c != connection
            if condition:
                try:
                    c.send(message.encode())
                except AttributeError:
                    c.send(message)
                except:
                    c.close()
                    remove.append(c)
        for c in remove:
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
        # self.ip = retrieveIP()

        closed = False
        while not closed:
            sockets_list = [sys.stdin, self.s]

            read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

            for socks in read_sockets:
                if socks == self.s:
                    message = socks.recv(2048)
                    if message:
                        try:
                            print(message.decode())
                        except UnicodeDecodeError:
                            file = open("file","wb")
                            print("Downloading... 0 bytes",end="\r")
                            idx = 0
                            while message:
                                if idx % 2000 == 0:
                                    print("Downloading... {}             ".format(sizeof_fmt(2048*idx)), end="\r")
                                file.write(message)
                                idx += 1
                                ready = select.select([socks], [], [], 1)
                                if ready[0]:
                                    message = socks.recv(2048)
                                else:
                                    break
                            file.close()
                            print("Downloading... {} (done)      ".format(sizeof_fmt(2048*idx)))
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


def get_bcast_ip():
    ifconfig = os.popen("ifconfig | grep -Eo '(Bcast:)?(([0-9]+\.){3}255)' | grep -Eo '(([0-9]+\.){3}255)'").read()
    bcast = ifconfig.split("\n")[0]
    return bcast


def list_netips():
    selector = re.compile("^\? \({}\)".format(re_ip))
    broadcast_ip = get_bcast_ip()
    try:
        subprocess.check_output(["ping", "-i","0.1", "-c","2", broadcast_ip])
    except subprocess.CalledProcessError as e:
        try:
            subprocess.check_output(["ping", "-i","1", "-c","2", "-b", broadcast_ip])
        except subprocess.CalledProcessError as e:
            print("Failed. {}".format(str(e)))
            return False

    arps = subprocess.check_output(["arp", "-a"]).decode()
    ips = [re.match(selector, a) for a in arps.split('\n')]
    ips = [i.group(1) for i in ips if i]
    ip_start = '.'.join(broadcast_ip.split('.')[:-1])
    ips = [i+" (bcast)" if i == broadcast_ip else i for i in ips if i.startswith(ip_start)]
    return ips


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='target IP to connect to', type=str, dest="target")
    parser.add_argument('-p', help='port to listen (default 55555)', type=int, default=55555, dest="port")
    parser.add_argument('-l', '--listen', nargs='?', help='listen to [host]:[port] for incoming connections',
                        default=False, const=True)
    parser.add_argument("-a", "--arp", nargs='?',
                        help="list all IP addresses connected to your network (see who's online)",
                        dest="arp", default=False, const=True)
    args = parser.parse_args()

    if args.arp:
        ips = list_netips()
        if ips:
            print('\n'.join(ips))

    if args.listen:
        server = Server(args.port)
        print("Chat initiated with IP {} on port {}".format(server.ip, server.port))
        server.start()
    elif args.target:
        client = Client(args.target,args.port)




