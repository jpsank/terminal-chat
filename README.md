# terminal-chat
Chat with your friends on LAN through the terminal!

## Usage
```
usage: main.py [-h] [-t TARGET] [-p PORT] [-l [LISTEN]] [-a [ARP]]

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET             target IP to connect to
  -p PORT               port to listen (default 55555)
  -l [LISTEN], --listen [LISTEN]
                        listen to [host]:[port] for incoming connections
  -a [ARP], --arp [ARP]
                        list all IP addresses connected to the network (see who's online)
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
 - /help, /?                      display this help message
 - /pm [ip] [message]             send a message only to certain ip
 - /file [filepath]               download a file from the server
 - /alias [alias]                 set your name on this server (others will see this instead of your IP)
 - /members                       return all members of this chat
```
For example, if I wanted to send a message "hello, this message will only broadcast to you" to only the IP address 192.168.0.2, I would type:
```
/pm 192.168.0.2 hello, this message will only broadcast to you
```
If I wanted to make it so I would show up as "George" on any messages sent by me, I would type:
```
/alias George
```
So that servers can distribute files to their clients, a client can use the file command to grab files from the server, like so:
```
/file cat.jpg
Downloading... 3.1MiB (done)
```
On the client side, it will be saved as "file" in the program directory (extension must be added)

## Future Possibilities
- [x] Add the ability to send images over chat
- [ ] List all online LAN chat servers for easier connection (See who's online)
- [ ] Improve UI
