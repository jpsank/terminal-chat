import subprocess
import os
import argparse
import shlex


class Chat:
    def __init__(self,port):
        self.port = port
        self.ip = os.popen("""ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'""").read().strip()

    def start(self):
        os.system("while true; do nc -l {}; done".format(self.port))


def connect(target,port):
    ip = os.popen("""ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'""").read()
    while True:
        m = "{}>{}".format(ip,input(""))
        os.system('echo "{}" | nc {} {}'.format(m,target,port))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', help='target to listen', type=str, dest="target")
    parser.add_argument('-p', help='port to listen', type=int, default=55555, dest="port")
    parser.add_argument('-l', '--listen', nargs='?', help='listen to [host]:[port] for incoming connections',
                        default=False, const=True)
    args = parser.parse_args()

    if args.listen:
        chat = Chat(args.port)
        print("CHAT: ip {}, port {}".format(chat.ip,chat.port))
        chat.start()
    else:
        connect(args.target,args.port)


