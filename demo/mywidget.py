# -*- coding: utf-8 -*-


import os
import threading
import subprocess
from time import sleep

from expcatalyst.widget import Widget, Interrupted
from expcatalyst.builtin import ANCHOR_NUMBER, ANCHOR_NUMBERS

import mydialog as Di

MAIN_PATH = os.path.dirname(os.path.realpath(__file__))
Here = lambda f="": os.path.join(MAIN_PATH, f)


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


class SubprocessExample(Widget):
    NAME = "Subprocess Example"
    DIALOG = {"ORIENTATION": "V", "SIZE": (120, -1)}
    THREAD = True
    OUTGOING = ANCHOR_NUMBER

    def Task(self):
        t = threading.currentThread()
        p = subprocess.Popen(["python", Here("dummyprocess.py")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while p.poll() is None:
            sleep(1)
            if t.Stopped():
                p.kill()
                raise Interrupted
        if p.returncode == 0:
            return int(p.stdout.read())
