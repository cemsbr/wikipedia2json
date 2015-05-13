#!/usr/bin/env python3
import pstats

p = pstats.Stats('stats')
p.strip_dirs().sort_stats('tottime').print_stats()
