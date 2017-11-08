# -*- coding: utf-8 -*-

from ..widget import Widget, ANCHOR_ALL
from .anchor import AnchorFCFS

__all__ = [
    "Passer",
    "Condition",
    "Wait",
]


# ======================================================= Widget =======================================================
class Passer(Widget):
    NAME = "Passer"
    INCOMING = ANCHOR_ALL, "DATA", False, "LTBR", "Data to pass", AnchorFCFS
    OUTGOING = ANCHOR_ALL, "", AnchorFCFS

    def Task(self):
        return self["DATA"]


class Condition(Widget):
    NAME = "Condition"
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
    INCOMING = (ANCHOR_ALL, "DATA", False, "L", "Data to pass", AnchorFCFS), \
               (ANCHOR_ALL, "WAIT", True, "TB", "Tasks to wait")
    OUTGOING = ANCHOR_ALL, "", AnchorFCFS

    def Name(self):
        if self.IsState("Wait"):
            return "Waiting"
        if self.IsState("Done"):
            return "Pass"
        if self.IsState("Fail"):
            return "Failed"

    def Task(self):
        return self["DATA"]
