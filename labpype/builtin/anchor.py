# -*- coding: utf-8 -*-

from ..widget import Anchor, ANCHOR_ALL, LegitLink

__all__ = [
    "AnchorFCFS",
    "AnchorMixed",
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


class AnchorMixed(Anchor):
    def __index__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.multiple, "class <AnchorMixed> must allow multiple connections!"

    def Retrieve(self):
        if self.connected:
            data = []
            for dest in self.connected:
                d = dest.Widget[dest.key]
                if d is None:
                    data.append(None)
                    continue
                f = LegitLink.Transfer(dest.GetType(), self.GetType())
                if not isinstance(d, (tuple, list)):
                    d = [d]
                for _d in d:
                    if f is None:
                        data.append(_d)
                    elif callable(f):
                        data.append(f(_d))
                    else:
                        data.append(_d[f])
            return data
        return None
