#!/bin/bash

BRANCH=$1

DIRNAME="dev_${BRANCH//-/_}"
RESERVED_BIT=-1

echo $DIRNAME

function spin_up_dev {
    DIRNAME=$1
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
}

function deploy {
    echo "../${DIRNAME}"
    if [ ! -d "../${DIRNAME}" ]; then
        spin_up_dev $DIRNAME
    else
        cd "../${DIRNAME}"
    fi 

    RESERVED_BIT=$(head -n 1 bit.txt)
    let PORT="3334 + RESERVED_BIT"
    echo "Reserved port is: ${PORT}"

    cd TerminalMessenger
    git checkout $BRANCH
    git pull

    screen -X -S $DIRNAME quit
    screen -S $DIRNAME -m -d ./server.py $PORT
}

ssh tm@terminalmessenger.com "
cd TerminalMessenger/;
$(typeset -f spin_up_dev);
$(typeset -f deploy);
DIRNAME=${DIRNAME} deploy
";
