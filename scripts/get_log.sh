#!/bin/bash

LINES=10
FILE="debug.log"

if [ "$1" != "" ]; then
  LINES=$1
fi

if [ "$2" != "" ]; then
    FILE=$2
fi

ssh tm@terminalmessenger.com "
cd TerminalMessenger/;
tail -n $LINES $FILE
"
