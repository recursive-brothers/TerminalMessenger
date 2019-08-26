#!/bin/bash

ssh tm@terminalmessenger.com '
cd TerminalMessenger/;
killall screen;
git pull;
screen -m -d ./server.py 3333
'
