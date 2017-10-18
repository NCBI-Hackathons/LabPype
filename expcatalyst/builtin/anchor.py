# -*- coding: utf-8 -*-

from ..widget.link import *
from ..widget.anchor import Anchor

__all__ = [
    "ANCHOR_NUMBER", "ANCHOR_NUMBERS",
    "ANCHOR_TEXT", "ANCHOR_TEXTS",
    "ANCHOR_SSH",
    "AnchorFCFS",
]


# ======================================================= Anchor =======================================================
class AnchorFCFS(Anchor):
    def GetType(self):
        if self.connected:
            return self.connected[0].GetType()
        else:
            for a in self.Widget.Anchors:
                if a != self and isinstance(a, AnchorFCFS):
                    if a.connected:
                        return a.GetType()
            return ANCHOR_ALL


# ======================================================= Anchor =======================================================
class ANCHOR_NUMBER(ANCHOR_REGULAR): pass


class ANCHOR_NUMBERS(ANCHOR_REGULAR): pass


class ANCHOR_TEXT(ANCHOR_REGULAR): pass


class ANCHOR_TEXTS(ANCHOR_REGULAR): pass


class ANCHOR_SSH(ANCHOR_REGULAR): pass


for reverse, source, target in (
        (0, ANCHOR_NUMBER, ANCHOR_NUMBER),
        (0, ANCHOR_NUMBER, ANCHOR_NUMBERS),
        (0, ANCHOR_NUMBERS, ANCHOR_NUMBERS),

        (0, ANCHOR_TEXT, ANCHOR_TEXT),
        (0, ANCHOR_TEXT, ANCHOR_TEXTS),

        (0, ANCHOR_SSH, ANCHOR_SSH),
):
    LegitLink.Add(source, target, reverse)
