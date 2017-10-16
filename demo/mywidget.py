# -*- coding: utf-8 -*-


import threading
from expcatalyst.widget import Widget, Interrupted
from expcatalyst.builtin import ANCHOR_NUMBER, ANCHOR_NUMBERS

import mydialog as Di

from time import sleep


class Summer(Widget):
    NAME = "Summer"
    DIALOG = Di.Number
    THREAD = True
    INTERNAL = None
    INCOMING = ANCHOR_NUMBERS, "NUMBERS", True, "LTB", "Number"
    OUTGOING = ANCHOR_NUMBER

    def Name(self):
        if self.IsDone():
            return "+".join(str(i) for i in self["NUMBERS"]) + "=" + str(self["OUT"])

    def Task(self):
        t = threading.currentThread()
        p = 0
        for i in self["NUMBERS"]:
            sleep(0.5)
            if t.Stopped():
                raise Interrupted
            p += i
        return p


class Multiplier(Widget):
    NAME = "Multiplier"
    DIALOG = Di.Number
    THREAD = True
    INTERNAL = None
    INCOMING = ANCHOR_NUMBERS, "NUMBERS", True, "LTB", "Number"
    OUTGOING = ANCHOR_NUMBER

    def Name(self):
        if self.IsDone():
            return "*".join(str(i) for i in self["NUMBERS"]) + "=" + str(self["OUT"])

    def Task(self):
        t = threading.currentThread()
        p = 1
        for i in self["NUMBERS"]:
            sleep(1)
            if t.Stopped():
                raise Interrupted
            p *= i
        return p
