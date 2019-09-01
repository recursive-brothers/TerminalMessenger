#!/bin/bash

find . -name "*test.py" | xargs -n1 python3
find . -path ./tests -prune -o -name "*.py" -print | xargs -n1 mypy
