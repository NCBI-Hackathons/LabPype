# -*- coding: utf-8 -*-

from ..widget import Widget, ANCHOR_ALL
from .anchor import AnchorFCFS
import threading

__all__ = [
    "Merge",
    "Filter",
]


class Merge(Widget):
    NAME = "Merge"
    THREAD = True
    INCOMING = ANCHOR_ALL, "DATA", True, "L", "Data to merge", AnchorFCFS
    OUTGOING = ANCHOR_ALL, "Merged", AnchorFCFS

    def Task(self):
        t = threading.currentThread()
        out = []
        total = len(self["DATA"])
        for index, data in enumerate(self["DATA"]):
            t.Checkpoint(index, total)
            if isinstance(data, (list, tuple)):
                out.extend(data)
            else:
                out.append(data)
        return out


class Filter(Widget):
    NAME = "Filter"
    THREAD = True
    INCOMING = (ANCHOR_ALL, "DATA", False, "L", "Data to filter", AnchorFCFS), \
               (ANCHOR_ALL, "RULE", False, "TB", "Function for filtering")
    OUTGOING = ANCHOR_ALL, "Filtered", AnchorFCFS

    def Task(self):
        t = threading.currentThread()
        out = []
        rule = self["RULE"]
        total = len(self["DATA"])
        for index, data in enumerate(self["DATA"]):
            t.Checkpoint(index, total)
            if rule(data):
                out.append(data)
        return out
