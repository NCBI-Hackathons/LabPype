# -*- coding: utf-8 -*-

from ..widget import Widget
from ..widget.field import *
from .anchor import *

__all__ = [
    "Number",
    "RandomInt",
]

# ======================================================= Widget =======================================================
from random import randint


class Number(Widget):
    NAME = "Number"
    DIALOG = "V"
    THREAD = False
    INTERNAL = FloatField(key="NUMBER", label="")
    INCOMING = None
    OUTGOING = ANCHOR_NUMBER

    def GetName(self):
        if self["OUT"] is not None:
            return str(self["OUT"])

    def Function(self):
        return self["NUMBER"]


class RandomInt(Widget):
    NAME = "Random Integer"
    DIALOG = "V"
    THREAD = False
    INTERNAL = IntegerField(key="MIN", label="Min"), IntegerField(key="MAX", label="Max")
    INCOMING = None
    OUTGOING = ANCHOR_NUMBER

    def GetName(self):
        if self["OUT"] is not None:
            return str(self["OUT"])

    def Function(self):
        return randint(self["MIN"], self["MAX"])
