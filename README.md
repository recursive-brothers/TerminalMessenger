# The Terminal Messenger #

Chat server and client written with Python using sockets library :)

## Core Features ##
- [ ] message one on one with another client
- [ ] group messaging
	- [ ] public forums anyone can read and write messages to
	- [ ] private chatrooms which users add other users to
- [x] add names to messages
- [ ] Persistence
	- [ ] accounts for users
	- [ ] message history
- [ ] multi threaded server (for things like handling client handshake in own function, handling even more messages/chatrooms,etc)
	- [ ] handling a client-server handshake
	- [ ] better performance and management for multiple messages/chatrooms

## Bonus Features ##
- [ ] App management:
	- [ ] packaging it with pypy
	- [ ] dockerize it 
	- [ ] have different subdomains for the different services of our application (e.g. http server)
	- [ ] script to scrape for all errors in server.log, or a certain number of them, like tail for errors (sed?)
	- [ ] horizontal scaling with a load balancer
	- [ ] add a domain name
- [ ] Terminal Client:
	- [x] formatting with ncurses
	- [ ] adding useful text commands (/join to join a chatroom, /l to list public chatrooms)
	- [ ] image rendering 
	- [ ] text search for previous messages
	- [ ] message scroll
	- [x] mouse up to get past messages and load previous messages on scroll
	- [ ] scrollable input area for long messages
	- [ ] input autocomplete(?)
	- [ ] emojis
	- [ ] split terminal for multiple chatrooms
	- [ ] autocomplete for text commands
	- [ ] sidebar with options for interacting with multiple chatrooms
	- [x] pretty colors :)
	- [x] add messages for users that connected/disconnected to the chatroom
	- [ ] speech recognition
- [ ] Terminal Server:
	- [ ] admin privileges to starters of group messages/chatrooms, etc.
	- [ ] hidden file with username and password saved to not type in username and password every time (almost like a cookie)
- [ ] Security:
	- [ ] encryption
	- [ ] security (blocking ips, etc)
	- [ ] prevent injection/other exploits to server
- [ ] HTTP Server:
	- [ ] user/message history
	- [ ] Data analytics (possibly integrated with the client by default?)
	- [ ] Full-text search
	- [ ] and more
- [ ] WebSockets Client:
	- [ ] gain the ability to send messages from terminal to browser client and vice versa
	- [ ] create a desktop app to accompany the browser version of the client
	- [ ] allow the ability to send images (convert images to ascii art for the terminal?)
	- [ ] integrate all other terminal client features
- [ ] static HTML page that we serve (with web server) about the project (until HTTP server server are established)