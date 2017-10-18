# -*- coding: utf-8 -*-

from ..widget import Widget, Anchor, ANCHOR_ALL
from ..widget.field import *
from .anchor import *

__all__ = [
    "Passer",
    "Condition",
    "Wait",
]


# ======================================================= Widget =======================================================
class Passer(Widget):
    NAME = "Passer"
    DIALOG = None
    THREAD = False
    INTERNAL = None
    INCOMING = ANCHOR_ALL, "DATA", False, "L", "Data to Pass", AnchorFCFS
    OUTGOING = ANCHOR_ALL, "", AnchorFCFS

    def Task(self):
        return self["DATA"]


class Condition(Widget):
    NAME = "Condition"
    DIALOG = None
    THREAD = False
    INTERNAL = None
    INCOMING = (ANCHOR_ALL, "TEST", False, "L", "Condition to test"), \
               (ANCHOR_ALL, "VALUE_T", False, "T", "Data passed if condition true ", AnchorFCFS), \
               (ANCHOR_ALL, "VALUE_F", False, "B", "Data passed if condition false", AnchorFCFS)
    OUTGOING = ANCHOR_ALL, "", AnchorFCFS

    def Name(self):
        if self["TEST"] is not None:
            return "Passing Top" if bool(self["TEST"]) else "Passing Bottom"

    def Task(self):
        return self["VALUE_T"] if bool(self["TEST"]) else self["VALUE_F"]


class Wait(Widget):
    NAME = "Wait"
    DIALOG = None
    THREAD = False
    INTERNAL = None
    INCOMING = (ANCHOR_ALL, "DATA", False, "L", "Data to Pass", AnchorFCFS), \
               (ANCHOR_ALL, "WAIT", True, "TB", "Tasks to wait")
    OUTGOING = ANCHOR_ALL, "", AnchorFCFS

    def Name(self):
        if self.IsWaiting():
            return "Waiting"
        if self.IsDone():
            return "Pass"
        if self.IsFailed():
            return "Failed"

    def Task(self):
        return self["DATA"]
