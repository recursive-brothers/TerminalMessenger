#!/bin/bash

LINES=10

if [ "$1" != "" ]; then
  LINES=$1
fi

SCRIPT='
cd TerminalMessenger/;
tail -n $(echo $LINES) server.log
'

echo $SCRIPT

ssh tm@18.222.230.158 "
cd TerminalMessenger/;
tail -n $LINES server.log
"