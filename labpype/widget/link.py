# -*- coding: utf-8 -*-

__all__ = [
    "LegitLink",
    "ANCHOR_REGULAR",
    "ANCHOR_SPECIAL",
    "ANCHOR_ALL",
    "ANCHOR_NONE"
]


# =============================================== AnchorType & LegitLink ===============================================
class ANCHOR_REGULAR(object):
    pass


class ANCHOR_SPECIAL(object):
    pass


class ANCHOR_ALL(ANCHOR_SPECIAL):
    pass


class ANCHOR_NONE(ANCHOR_SPECIAL):
    pass


class _LegitLink(object):
    _SharedState = {}

    def __init__(self):
        self.__dict__ = self._SharedState
        self.links = {}

    def __call__(self, a1, a2):  # TODO deal with subclass
        if issubclass(a1.aType, ANCHOR_SPECIAL) and issubclass(a2.aType, ANCHOR_SPECIAL):
            return False
        if a1.GetType() == ANCHOR_NONE or a2.GetType() == ANCHOR_NONE:
            return False
        if a1.GetType() == ANCHOR_ALL or a2.GetType() == ANCHOR_ALL:
            return a1.send != a2.send
        if a1.recv and a2.send:
            return a1.GetType() in self.links.get(a2.GetType(), {})
        if a1.send and a2.recv:
            return a2.GetType() in self.links.get(a1.GetType(), {})
        return False

    def Add(self, source, target, reverse=False):
        if source is target:
            reverse = False
        if source not in self.links:
            self.links[source] = {}
        if target not in self.links[source]:
            self.links[source][target] = 1
        else:
            self.links[source][target] += 1
        if reverse:
            self.Add(target, source, False)

    def Del(self, source, target, reverse=False):
        if source is target:
            reverse = False
        self.links[source][target] -= 1
        if self.links[source][target] == 0:
            del self.links[source][target]
        if not self.links[source]:
            del self.links[source]
        if reverse:
            self.Del(target, source, False)

    def AddBatch(self, links):
        for link in links:
            self.Add(link[1], link[2] if len(link) == 3 else link[1], link[0])

    def DelBatch(self, links):
        for link in links:
            self.Del(link[1], link[2] if len(link) == 3 else link[1], link[0])


LegitLink = _LegitLink()
