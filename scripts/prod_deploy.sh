#!/bin/bash

ssh tm@terminalmessenger.com '
cd TerminalMessenger/;
screen -X -S prod quit;
git pull;
screen -S prod -m -d ./server.py 3333
'
