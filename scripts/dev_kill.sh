#!/bin/bash

BRANCH=$1
DIRNAME="dev_${BRANCH//-/_}"

function kill_dev {
    if [ ! -d $DIRNAME ]; then
        echo "The directory ${DIRNAME} does not exist!"
        exit
    fi

    RESERVED_BIT=$(head -n 1 "${DIRNAME}/bit.txt")
    screen -X -S $DIRNAME quit
    rm -rf $DIRNAME

    cd TerminalMessenger
    BITMAP=$(head -n 1 bitmap.txt)
    (( BITMAP &= ~(1 << RESERVED_BIT) ))
    echo $BITMAP > bitmap.txt
}

ssh tm@terminalmessenger.com "
$(typeset -f kill_dev);
DIRNAME=${DIRNAME} kill_dev
"
