#!/bin/bash

BRANCH=$1

DIRNAME="dev_${BRANCH//-/_}"
RESERVED_BIT=-1

if [ ! -d "../${DIRNAME}" ]; then
    BITMAP=$(head -n 1 bitmap.txt)

    if [ $BITMAP == "" ]; then BITMAP="0"; fi

    if [ $BITMAP == "1023" ]; then
        echo "No dev slots remain!"
        exit
    fi

    for i in {0..9}; do
        if [ $(( BITMAP & ( 1 << i ) )) -eq 0 ]; then
            (( BITMAP |= ( 1 << i ) ))
            echo $BITMAP > bitmap.txt
            RESERVED_BIT=$i
            echo "Looks like we end at ${i}!!!"
            break
        fi
    done

    mkdir "../${DIRNAME}"
    cd "../${DIRNAME}"
    echo $RESERVED_BIT > bit.txt
    git clone https://github.com/recursive-brothers/TerminalMessenger.git
else 
    RESERVED_BIT=$(head -n 1 bit.txt)
    cd "../${DIRNAME}"
fi

let PORT="3334 + RESERVED_BIT"
echo "Reserved port is: ${PORT}"

cd TerminalMessenger
git checkout $BRANCH
git pull

screen -X -S $DIRNAME quit
screen -S $DIRNAME -m -d ./server.py $PORT
