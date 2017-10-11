# -*- coding: utf-8 -*-


import wx
from DynaUI import Singleton

__all__ = []


# ======================================================= IdPool =======================================================
class IdPool(object, metaclass=Singleton):
    SIZE = 4096

    def __init__(self):
        self.Id = list(range(self.SIZE))

    def Acquire(self):
        if len(self.Id):
            return self.Id.pop(0)
        else:
            raise Exception

    def Release(self, id_):
        self.Id.insert(0, id_)


IdPool = IdPool()


# ======================================================== Base ========================================================
class Base(object):
    def __init__(self, w, h):
        self.Id = IdPool.Acquire()
        self.x = self.lastX = 0
        self.y = self.lastY = 0
        self.rect = wx.Rect(0, 0, w, h)
        self.Contains = self.rect.Contains

    def GetPosition(self):
        return self.x, self.y

    def SavePosition(self):
        self.lastX = self.x
        self.lastY = self.y

    def RePosition(self, dx, dy):
        self.NewPosition(dx + self.lastX, dy + self.lastY)

    def SetPosition(self, x, y):
        self.NewPosition(x, y)
        self.SavePosition()

    def NewPosition(self, x, y):
        raise NotImplementedError
