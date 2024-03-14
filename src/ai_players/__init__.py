import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from .multi_arm_guesser import *
from .multi_arm_spymaster import *
