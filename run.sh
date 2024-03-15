#!/bin/sh

CURRENT_DIR=$(pwd)
export PYTHONPATH="$CURRENT_DIR:$CURRENT_DIR/src"

python3 src/start_bot.py