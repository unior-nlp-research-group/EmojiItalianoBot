# -*- coding: utf-8 -*-

import re
import textwrap


def makeArray2D(data_list, length=2):
    return [data_list[i:i+length] for i in range(0, len(data_list), length)]


def distributeElementMaxSize(seq, maxSize=5):
    lines = len(seq) / maxSize
    if len(seq) % maxSize > 0:
        lines += 1
    avg = len(seq) / float(lines)
    out = []
    last = 0.0
    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg
    return out

def unindent(s):
    return re.sub('[ ]+', ' ', textwrap.dedent(s))
