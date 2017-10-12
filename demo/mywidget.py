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
    INCOMING = ANCHOR_NUMBERS, "NUMBERS", True, "L", "Number"
    OUTGOING = ANCHOR_NUMBER

    def GetName(self):
        return "+".join(str(i) for i in self["NUMBERS"]) + "=" + str(self["OUT"]) if self.IsDone() else self.NAME

    def Function(self):
        sleep(1)
        return sum(self["NUMBERS"])


class Multiplier(Widget):
    NAME = "Multiplier"
    DIALOG = Di.Number
    THREAD = True
    INTERNAL = None
    INCOMING = ANCHOR_NUMBERS, "NUMBERS", True, "L", "Number"
    OUTGOING = ANCHOR_NUMBER

    def GetName(self):
        return "*".join(str(i) for i in self["NUMBERS"]) + "=" + str(self["OUT"]) if self.IsDone() else self.NAME

    def Function(self):
        t = threading.currentThread()
        p = 1
        for i in self["NUMBERS"]:
            sleep(1)
            if t.Stopped():
                raise Interrupted
            p *= i
        return p
