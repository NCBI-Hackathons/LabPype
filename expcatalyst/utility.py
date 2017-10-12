# -*- coding: utf-8 -*-


import os

MAIN_PATH = os.path.dirname(os.path.realpath(__file__))
Here = lambda path="", f="": os.path.join(os.path.join(MAIN_PATH, path), f)


def avg(data):
    return sum(data) / len(data)


def AlignT(posList):
    v = min([y for x, y in posList])
    return [(x, v) for x, y in posList]


def AlignH(posList):
    v = avg([y for x, y in posList])
    return [(x, v) for x, y in posList]


def AlignB(posList):
    v = max([y for x, y in posList])
    return [(x, v) for x, y in posList]


def AlignL(posList):
    h = min([x for x, y in posList])
    return [(h, y) for x, y in posList]


def AlignV(posList):
    h = avg([x for x, y in posList])
    return [(h, y) for x, y in posList]


def AlignR(posList):
    h = max([x for x, y in posList])
    return [(h, y) for x, y in posList]


def DistributeH(posList):
    if len(posList) <= 2:
        return posList
    x = sorted([i for i, j in posList])
    interval = (x[-1] - x[0]) / (len(posList) - 1)
    return [(x[0] + interval * i, posList[i][1]) for i in range(len(posList))]


def DistributeV(posList):
    if len(posList) <= 2:
        return posList
    y = [j for i, j in posList]
    y.sort()
    interval = (y[-1] - y[0]) / (len(posList) - 1)
    return [(posList[i][0], y[0] + interval * i) for i in range(len(posList))]
