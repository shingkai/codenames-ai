#!/bin/sh

CURRENT_DIR=$(pwd)
export PYTHONPATH="$CURRENT_DIR:$CURRENT_DIR/codenames_ai/"

python3 codenames/start_bot.py