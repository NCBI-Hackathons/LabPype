# -*- coding: utf-8 -*-

from ..widget import Anchor, ANCHOR_ALL

__all__ = [
    "AnchorFCFS",
]


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
