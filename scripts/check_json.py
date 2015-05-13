#!/usr/bin/env python3
import json
import fileinput
import sys

for line in fileinput.input():
    try:
        json.loads(line)
        print(line)
    except:
        print(line, file=sys.stderr)

print('{} json lines verified.'.format(fileinput.lineno()), file=sys.stderr)
