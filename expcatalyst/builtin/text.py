# -*- coding: utf-8 -*-

from ..widget import Widget
from ..widget.field import *
from .anchor import *

__all__ = [
    "Line",
    "Text",
]


# ======================================================= Widget =======================================================
class Line(Widget):
    NAME = "Line"
    DIALOG = {"ORIENTATION": "H", "SIZE": (400, -1)}
    THREAD = False
    INTERNAL = LineField(key="TEXT", label="")
    INCOMING = None
    OUTGOING = ANCHOR_TEXT

    def Function(self):
        return self["TEXT"]

    def IsInternalAvailable(self):
        if self["TEXT"] is None:
            self["TEXT"] = ""
        return True


class Text(Widget):
    NAME = "Text"
    DIALOG = {"ORIENTATION": "V", "SIZE": (400, 400)}
    THREAD = False
    INTERNAL = LineField(key="NAME", label="", hint="Input Widget Name Here"), TextField(key="TEXT", label="")
    INCOMING = None
    OUTGOING = ANCHOR_TEXT

    def GetName(self):
        return self["NAME"]

    def Function(self):
        return self["TEXT"]

    def IsInternalAvailable(self):
        if self["NAME"] is None:
            self["NAME"] = ""
        if self["TEXT"] is None:
            self["TEXT"] = ""
        return True
