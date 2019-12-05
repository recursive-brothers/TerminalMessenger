#!/bin/bash

# what needs to happen?
# the pattern is:
# 1. somebody pushes code from a branch
# 2. we get that branch name and execute the below code with that branch name on the server
# 3. I think there needs to be one script that kicks it off and the other that does the server work


BRANCH=$(git symbolic-ref HEAD 2>/dev/null)
BRANCH=${BRANCH##refs/heads/}

DIRNAME="dev_${BRANCH//-/_}"
RESERVED_BIT="-1"

if [ ! -d "${DIRNAME}" ]; then
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
            echo $RESERVED_BIT > bit.txt
            echo "Looks like we end at ${i}!!!"
            break
        fi
    done
else 
    RESERVED_BIT=$(head -n 1 bit.txt)
fi


let PORT="3334 + RESERVED_BIT"
echo "Reserved port is: ${PORT}"

mkdir $DIRNAME
cd $DIRNAME

git clone https://github.com/recursive-brothers/TerminalMessenger.git
git checkout $BRANCH
git pull

screen -X -S "dev${RESERVED_BIT}" quit
screen -S "dev${RESERVED_BIT}" -m -d ./server.py $PORT

