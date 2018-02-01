# -*- coding: utf-8 -*-

import wx

__all__ = []


# ======================================================= IdPool =======================================================
class _IdPool(object):
    _SharedState = {}

    def __init__(self):
        self.__dict__ = self._SharedState
        self.Id = list(range(4096))

    def Acquire(self):
        if len(self.Id):
            return self.Id.pop(0)
        else:
            raise Exception

    def Release(self, id_):
        self.Id.insert(0, id_)


IdPool = _IdPool()


# ======================================================== Base ========================================================
class Base(object):
    __TYPE__ = "BASE"

    def __init__(self, w, h):
        self.AcquireID()
        self.x = self.lastX = 0
        self.y = self.lastY = 0
        self.rect = wx.Rect(0, 0, w, h)
        self.Contains = self.rect.Contains

    def AcquireID(self):
        self.Id = IdPool.Acquire()

    def ReleaseID(self):
        IdPool.Release(self.Id)

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
