#!/bin/bash

find . -name "*test.py" | xargs -n1 python3
find . -name "*.py" | xargs -n1 mypy
