#!/usr/bin/env python3
#
# natural_sort.py
# Natural sort thanks to Mark Byers in StackOverflow

import re

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key= lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)
