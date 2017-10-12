# -*- coding: utf-8 -*-

from ..widget import Widget, Anchor, ANCHOR_ALL
from ..widget.field import *
from .anchor import *

__all__ = [
    "Passer",
    "Condition",
]


# ======================================================= Widget =======================================================
class Passer(Widget):
    NAME = "Passer"
    DIALOG = None
    THREAD = False
    INTERNAL = None
    INCOMING = ANCHOR_ALL, "DATA", False, "L", "", AnchorFCFS
    OUTGOING = ANCHOR_ALL, "", AnchorFCFS

    def Function(self):
        return self["DATA"]


class Condition(Widget):
    NAME = "Condition"
    DIALOG = None
    THREAD = False
    INTERNAL = None
    INCOMING = (ANCHOR_ALL, "TEST", False, "L", "Condition to test"), \
               (ANCHOR_ALL, "VALUE_T", False, "T", "Value passed if condition true ", AnchorFCFS), \
               (ANCHOR_ALL, "VALUE_F", False, "B", "Value passed if condition false", AnchorFCFS)
    OUTGOING = ANCHOR_ALL, "", AnchorFCFS

    def GetName(self):
        if self["TEST"] is not None:
            return "T: Sending Top" if bool(self["TEST"]) else "F: Sending Bottom"
        return self.NAME

    def Function(self):
        return self["VALUE_T"] if bool(self["TEST"]) else self["VALUE_F"]
