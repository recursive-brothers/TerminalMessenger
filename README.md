# The Terminal Messenger #

Chat server and client written with Python using sockets library :)

roadmap:

TODO: 

core features:
- message one on one with another client
- group messaging
    - public forums anyone can read and write messages to
    - private chatrooms which users add other users to
- add names to messages
- accounts (data persistance)
- message history


bonus features:
- formatting with ncurses
- encryption
- packaging it with pypy
- dockerize it 
- adding useful text commands (/join to join a chatroom, /l to list public chatrooms)
- pretty colors :)
- analysis of your message history
- admin privileges to starters of group messages/chatrooms, etc.
- image rendering 
- security (blocking ips,etc)
- text search for previous messages
- mouse up to get past messages
- scrollable text area
- input autocomplete
- emojis
- HTTP server that serves:
	- user/message history
	- Data analytics
	- Full-text search
	- and more
- create additional clients using WebSockets to communicate with
	- gain the ability to send messages from terminal to browser client and vice versa
	- create a desktop app to accompany the browser version of the client
	- allow the ability to send images (convert images to ascii art for the terminal)
- additional Terminal Client features:
	- split terminal for multiple chatrooms
	- autocomplete for text commands
	- sidebar with options for interacting with multiple chatrooms
