#!/bin/bash

BRANCH=$1

DIRNAME="dev_${BRANCH//-/_}"

if [ ! -d "../${DIRNAME}" ]; then
    echo "The directory ${DIRNAME} does not exist!"
    exit
fi

cd "../${DIRNAME}"

RESERVED_BIT=$(head -n 1 bit.txt)

screen -X -S $DIRNAME quit

cd ..
rm -rf $DIRNAME

cd TerminalMessenger

BITMAP=$(head -n 1 bitmap.txt)

(( BITMAP &= (~1 << RESERVED_BIT) ))

echo $BITMAP > bitmap.txt
