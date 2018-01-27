import os
import argparse
import threading


def get_ip():
    process = os.popen("""ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'""")
    ip = process.read().strip().replace('\n',"")
    process.close()
    return ip


class Chat:
    def __init__(self,port):
        self.port = port
        self.ip = get_ip()

    def start(self):
        os.system("while true; do nc -l {} -k; done".format(self.port))


def connect(target,port):
    ip = get_ip()
    while True:
        # m = "{}>{}".format(ip, input("you>"))
        os.system('''nc {} {}'''.format(target, port))


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


