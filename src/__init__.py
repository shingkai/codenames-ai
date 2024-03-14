import os
import sys
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

logging.basicConfig(level=logging.INFO)
