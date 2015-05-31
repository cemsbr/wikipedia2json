#!/usr/bin/env python3.4
import sys


def str_to_bytes(size_str):
    unit = size_str[-1].upper()
    if unit == 'G':
        return int(size_str[:-1]) * 1024 * 1024 * 1024
    elif unit == 'M':
        return int(size_str[:-1]) * 1024 * 1024
    elif unit == 'K':
        return int(size_str[:-1]) * 1024
    else:
        return int(size_str)

max_size = str_to_bytes(sys.argv[1])

size = 0
for line in sys.stdin:
    size += len(line.encode())
    if size < max_size:
        print(line, end='')
    elif size == max_size:
        print(line, end='')
        sys.exit(0)
    else:
        sys.exit(0)
