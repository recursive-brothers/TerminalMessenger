#!/bin/bash

ssh tm@18.222.230.158 '
cd TerminalMessenger/;
killall screen;
git pull;
screen -m -d ./server.py 3333
'
