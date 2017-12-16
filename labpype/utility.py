# -*- coding: utf-8 -*-

import os
import threading

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
Find = lambda path="", f="": os.path.join(os.path.join(PACKAGE_PATH, path), f)


def AlignT(posList):
    v = min(y for x, y in posList)
    return [(x, v) for x, y in posList]


def AlignH(posList):
    v = sum(y for x, y in posList) / len(posList)
    return [(x, v) for x, y in posList]


def AlignB(posList):
    v = max(y for x, y in posList)
    return [(x, v) for x, y in posList]


def AlignL(posList):
    h = min(x for x, y in posList)
    return [(h, y) for x, y in posList]


def AlignV(posList):
    h = sum(x for x, y in posList) / len(posList)
    return [(h, y) for x, y in posList]


def AlignR(posList):
    h = max(x for x, y in posList)
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


class Interrupted(Exception):
    """Raise to interrupt running thread"""


class Thread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDaemon(True)
        self.stop = False
        self.status = ""
        self.progress = 0

    def Stop(self):
        self.stop = True

    def Checkpoint(self, status="", progress=0):
        if self.stop:
            raise Interrupted
        self.status = status
        self.progress = progress
        return True
