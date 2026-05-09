import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/elvis/projects/smart_home_take_home_assignment/install/dorm_lighting'
