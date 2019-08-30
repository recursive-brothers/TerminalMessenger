#!/bin/bash

LINES=10

if [ "$1" != "" ]; then
  LINES=$1
fi

ssh tm@terminalmessenger.com "
cd TerminalMessenger/;
tail -n $LINES server.log
"