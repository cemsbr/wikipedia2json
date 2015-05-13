#!/usr/bin/env python3
#
# Reads from standard input and writes to 1 file at a time up to its given
# size.
#
# For example, to save the 1st gigabyte of wikipedia dump to one file and
# the 2nd and 3rd to a second file:
# $ bzcat enwiki-20150304-pages-articles.json.bz2 | \
#     ./split 1G enwiki-1G.spl.json \  # 1GB file
#             3G enwiki-3G.spl.json \  # 2GB file
#
# Then, to cat the first 3GB of data:
# $ cat enwiki-1G.spl.json enwiki-3G.spl.json
#
import sys
from collections import namedtuple

FileParams = namedtuple('FileParams', ['size', 'file'])


def str_to_bytes(size_str):
    unit = size_str[-1]
    if unit == 'G':
        return int(size_str[:-1]) * 1024 * 1024 * 1024
    elif unit == 'M':
        return int(size_str[:-1]) * 1024 * 1024
    elif unit == 'K':
        return int(size_str[:-1]) * 1024
    else:
        return int(size_str)


files = []
for i in range(1, len(sys.argv), 2):
    size_str, filename = sys.argv[i:i + 2]
    size = str_to_bytes(size_str)
    files.append(FileParams(size, open(filename, 'w')))
files.sort(key=lambda f: f.size, reverse=True)


def get_next_file(files, size):
    """Returns the output file with the minimum file size that is larger or
       equals to the read size"""
    while files:
        file = files.pop()
        if file.size >= size:
            return file
        else:
            print('Not enough file size difference')
            file.file.close()
    return None


size = 0
file = files.pop()
for line in sys.stdin:
    size += len(line.encode())
    if size <= file.size:
        file.file.write(line)
    else:
        file.file.close()
        print(file.file.name + ' finished.')
        file = get_next_file(files, size)
        if file:
            file.file.write(line)
        else:
            break
