#!/bin/bash

BRANCH=$(git symbolic-ref HEAD 2>/dev/null)
BRANCH=${BRANCH##refs/heads/}

ssh tm@terminalmessenger.com "
cd TerminalMessenger/;
./scripts/start_dev_helper.sh ${BRANCH}
"
