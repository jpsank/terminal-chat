# terminal-chat
Chat with your friends on LAN through the terminal!

## Usage
```
usage: main.py [-h] [-t TARGET] [-p PORT] [-l [LISTEN]]

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET             target IP to connect to
  -p PORT               port to listen (default 55555)
  -l [LISTEN], --listen [LISTEN]
                        listen to [host]:[port] for incoming connections
```
### Server
If you want to host a chat server and listen for connections, type
```
python3 main.py -l
```
On a specific port (default 55555),
```
python3 main.py -p 12345 -l
```
The server is the central hub for messages, receiving messages and broadcasting them.
### Client
If you want to join an existing chat, simpy enter the server's IP address
```
python3 main.py -t 192.168.0.1
```
Or if it's on a specific port (default 55555), enter that too:
```
python3 main.py -t 192.168.0.1 -p 12345
```
Clients send messages to the server, which will then broadcast the messages to all of its other clients
### Chat Commands
Type "/help" in the chat to get help for chat commands
```
/help, /?                      display this help message
/pm [ip] [message]             send a message only to certain ip
/alias [ip] [alias]            set a temporary alias for an IP address
```
For example, if I wanted to send a message "hello, this message will only broadcast to you" to only the IP address 192.168.0.2, I would type:
```
/pm 192.168.0.2 hello, this message will only broadcast to you
```
If I wanted to make it so 192.168.0.2 would show up as "George" on any messages sent by him, I would type:
```
/alias 192.168.0.2 George
```

## Future Possibilities
- [ ] Add the ability to send images over chat
- [ ] Improve UI
