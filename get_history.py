#!/usr/bin/env python

"""
    extract the history crash info about the cegui and lua
"""

import sys
from app.utils import collect_history_data, collect_oneday

if __name__ == '__main__':
    if len(sys.argv) > 1:
        collect_oneday(sys.argv[1])
    else:
        collect_history_data()
