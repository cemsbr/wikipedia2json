#!/usr/bin/env python3
from wiki2json import Wiki2Json
import fileinput

w2j = Wiki2Json()
for line in fileinput.input():
    w2j.parse_line(line)
