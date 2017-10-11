# -*- coding: utf-8 -*-


from DynaUI import Singleton

__all__ = ["LegitLink", "ANCHOR_REGULAR", "ANCHOR_SPECIAL", "ANCHOR_ALL", "ANCHOR_NONE"]


# =============================================== AnchorType & LegitLink ===============================================
class ANCHOR_REGULAR(object):
    pass


class ANCHOR_SPECIAL(object):
    pass


class ANCHOR_ALL(ANCHOR_SPECIAL):
    pass


class ANCHOR_NONE(ANCHOR_SPECIAL):
    pass


class _LegitLink(object, metaclass=Singleton):
    def __init__(self):
        self.links = {}

    def __call__(self, a1, a2):
        if issubclass(a1.aType, ANCHOR_SPECIAL) and issubclass(a2.aType, ANCHOR_SPECIAL):
            return False
        if a1.GetType() == ANCHOR_NONE or a2.GetType() == ANCHOR_NONE:
            return False
        if a1.GetType() == ANCHOR_ALL or a2.GetType() == ANCHOR_ALL:
            return a1.send != a2.send
        if a1.recv and a2.send:
            return a1.GetType() in self.links.get(a2.GetType(), ())
        if a1.send and a2.recv:
            return a2.GetType() in self.links.get(a1.GetType(), ())
        return False

    def Add(self, source, target, reverse=True):
        if source not in self.links:
            self.links[source] = [target]
        elif target not in self.links[source]:
            self.links[source].append(target)
        if reverse:
            self.Add(target, source, False)


LegitLink = _LegitLink()
