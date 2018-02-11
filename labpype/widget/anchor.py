# -*- coding: utf-8 -*-

import wx
from .base import Base
from .link import LegitLink, Link

__all__ = ["Anchor"]

# ==================================================== Anchor Misc =====================================================
ANCHOR_STATE_IDLE = 1 << 0
ANCHOR_STATE_PASS = 1 << 1
ANCHOR_STATE_FAIL = 1 << 2

POS_TABLE = {
    1 : {-3: 'B', -2: 'B', -1: 'B', 0: 'B', 1: 'B', 2: 'B', 3: 'B', 4: 'B'},
    2 : {-3: 'R', -2: 'R', -1: 'R', 0: 'R', 1: 'R', 2: 'R', 3: 'R', 4: 'R'},
    3 : {-3: 'B', -2: 'R', -1: 'R', 0: 'R', 1: 'R', 2: 'B', 3: 'B', 4: 'B'},
    4 : {-3: 'T', -2: 'T', -1: 'T', 0: 'T', 1: 'T', 2: 'T', 3: 'T', 4: 'T'},
    5 : {-3: 'T', -2: 'T', -1: 'T', 0: 'T', 1: 'B', 2: 'B', 3: 'B', 4: 'B'},
    6 : {-3: 'T', -2: 'T', -1: 'T', 0: 'R', 1: 'R', 2: 'R', 3: 'R', 4: 'T'},
    7 : {-3: 'T', -2: 'T', -1: 'T', 0: 'R', 1: 'R', 2: 'B', 3: 'B', 4: 'B'},
    8 : {-3: 'L', -2: 'L', -1: 'L', 0: 'L', 1: 'L', 2: 'L', 3: 'L', 4: 'L'},
    9 : {-3: 'L', -2: 'L', -1: 'L', 0: 'B', 1: 'B', 2: 'B', 3: 'B', 4: 'L'},
    10: {-3: 'L', -2: 'L', -1: 'R', 0: 'R', 1: 'R', 2: 'R', 3: 'L', 4: 'L'},
    11: {-3: 'L', -2: 'L', -1: 'R', 0: 'R', 1: 'R', 2: 'B', 3: 'B', 4: 'L'},
    12: {-3: 'L', -2: 'T', -1: 'T', 0: 'T', 1: 'T', 2: 'L', 3: 'L', 4: 'L'},
    13: {-3: 'L', -2: 'T', -1: 'T', 0: 'T', 1: 'B', 2: 'B', 3: 'B', 4: 'L'},
    14: {-3: 'L', -2: 'T', -1: 'T', 0: 'R', 1: 'R', 2: 'R', 3: 'L', 4: 'L'},
    15: {-3: 'L', -2: 'T', -1: 'T', 0: 'R', 1: 'R', 2: 'B', 3: 'B', 4: 'L'}}


def DetectCircularReference(Incoming, Outgoing, visited=None):
    if visited is None: visited = []
    for a in Incoming.Outgoing:
        for dest in a.connected:
            if dest.Widget.Id not in visited:
                visited.append(dest.Widget.Id)
                if dest.Widget == Outgoing or DetectCircularReference(dest.Widget, Outgoing, visited):
                    return True


# ======================================================= Anchor =======================================================
class Anchor(Base):
    __TYPE__ = "ANCHOR"

    def __init__(self, widget, aType, key, multiple, send, pos, name):
        super().__init__(w=6, h=6)
        self.Widget = widget
        self.Canvas = widget.Canvas
        self.aType = aType
        self.key = key
        self.multiple = multiple
        self.send = send
        self.name = name
        self.pos = self.posDefault = pos[0]
        self.posTable = POS_TABLE[(0b1000 if "L" in pos else 0) |
                                  (0b0100 if "T" in pos else 0) |
                                  (0b0010 if "R" in pos else 0) |
                                  (0b0001 if "B" in pos else 0)]
        self.single = not multiple
        self.recv = not send
        self.rect.SetSize((18, 18))
        self.area = (0, 0, 6, 6)
        self.pointing = None
        self.leftPos = None
        if self.send:
            self.DrawFunctions = {ANCHOR_STATE_IDLE: self.DrawOutgoing,
                                  ANCHOR_STATE_PASS: self.DrawPassR,
                                  ANCHOR_STATE_FAIL: self.DrawFailR}
        elif self.multiple:
            self.DrawFunctions = {ANCHOR_STATE_IDLE: self.DrawIdleR,
                                  ANCHOR_STATE_PASS: self.DrawPassR,
                                  ANCHOR_STATE_FAIL: self.DrawFailR}
        else:
            self.DrawFunctions = {ANCHOR_STATE_IDLE: self.DrawIdleE,
                                  ANCHOR_STATE_PASS: self.DrawPassE,
                                  ANCHOR_STATE_FAIL: self.DrawFailE}
        self.SetState(ANCHOR_STATE_IDLE)
        self.connected = []

    def SetState(self, state):
        self.state = state
        self.Draw = self.DrawFunctions[state]

    def NewPosition(self, x, y):
        self.x = x
        self.y = y
        self.rect.SetPosition((x - 6, y - 6))
        self.area = (self.x, self.y, 6, 6)

    # ----------------------------------------------------------
    def DrawOutgoing(self, dc):
        dc.anchorOutgoing.append(self.area)

    def DrawIdleR(self, dc):
        dc.anchorIdleR.append(self.area)

    def DrawPassR(self, dc):
        dc.anchorPassR.append(self.area)

    def DrawFailR(self, dc):
        dc.anchorFailR.append(self.area)

    def DrawIdleE(self, dc):
        dc.anchorIdleE.append(self.area)

    def DrawPassE(self, dc):
        dc.anchorPassE.append(self.area)

    def DrawFailE(self, dc):
        dc.anchorFailE.append(self.area)

    # ----------------------------------------------------------
    def HandleMouse(self, evtType, evtPos):
        if evtType in (wx.wxEVT_LEFT_DOWN, wx.wxEVT_LEFT_DCLICK):
            self.Canvas.TempLink = [(self.x + 3, self.y + 3), None, None, self.send]
        elif evtType == wx.wxEVT_LEFT_UP:
            self.Canvas.TempLink = None
            self.SetState(ANCHOR_STATE_IDLE)
            self.leftPos = None
            if self.pointing:
                if LegitLink(self.pointing, self):
                    self.pointing.SetTarget(self) if self.pointing.send else self.SetTarget(self.pointing)
                self.pointing.SetState(ANCHOR_STATE_IDLE)
                self.pointing = None
        elif evtType == wx.wxEVT_MOTION:
            self.Canvas.HandleMouseMotion(evtPos)
            self.leftPos = evtPos
            pointing = None
            state = ANCHOR_STATE_IDLE
            if self.Canvas.Hovered == self.Widget or self.Canvas.Hovered in self.Widget.Anchors:
                pass
            elif getattr(self.Canvas.Hovered, "__TYPE__", None) == "WIDGET":
                for a in self.Canvas.Hovered.Anchors:
                    if LegitLink(a, self):
                        if a.multiple or not a.connected:
                            pointing = a
                            state = ANCHOR_STATE_PASS
                            break
            elif isinstance(self.Canvas.Hovered, Anchor):
                pointing = self.Canvas.Hovered
                state = ANCHOR_STATE_PASS if LegitLink(pointing, self) else ANCHOR_STATE_FAIL
            if pointing != self.pointing:
                if self.pointing:
                    self.pointing.SetState(ANCHOR_STATE_IDLE)
                self.pointing = pointing
                self.SetState(state)
            if self.pointing:
                self.pointing.SetState(state)
                self.leftPos = (self.pointing.x + 3, self.pointing.y + 3)
            self.Canvas.TempLink[1] = self.leftPos
            self.Canvas.TempLink[2] = (self.leftPos[0] - 0.5, self.leftPos[1] - 0.5)

    # ----------------------------------------------------------
    def EmptyTarget(self):
        for dest in self.connected.copy():
            self.RemoveTarget(dest)

    def RemoveTarget(self, dest):
        self.connected.remove(dest)
        dest.connected.remove(self)
        if self.send:
            del self.Canvas.Link[self.Id << 12 | dest.Id]
            dest.Widget.OnRemoveIncoming(dest.key, self.Widget)
            self.Widget.OnRemoveOutgoing(self.key, dest.Widget)
        else:
            del self.Canvas.Link[self.Id | dest.Id << 12]
            self.Widget.OnRemoveIncoming(self.key, dest.Widget)
            dest.Widget.OnRemoveOutgoing(dest.key, self.Widget)

    def SetTarget(self, dest, evt=True):  # self always send, dest always recv
        if DetectCircularReference(dest.Widget, self.Widget):  # Check the opposite send
            return self.Canvas.F.SetStatus(self.Canvas.L["MSG_CIRCULAR_LINKAGE"], 1, 5)
        if dest in self.connected:
            return self.RemoveTarget(dest)
        if dest.single and dest.connected:
            dest.EmptyTarget()
        if self.single and self.connected:
            self.EmptyTarget()
        self.connected.append(dest)
        dest.connected.append(self)
        if evt:
            self.Widget.OnAcceptOutgoing(self.key, dest.Widget)
            dest.Widget.OnAcceptIncoming(dest.key, self.Widget)
        rgb = self.Id << 12 | dest.Id
        pen = wx.Pen(wx.Colour((rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255), 11)
        self.Canvas.Link[rgb] = Link(self, dest, pen)

    def Retrieve(self):  # self always recv
        if self.connected:
            data = []
            for dest in self.connected:
                if dest.Widget[dest.key] is None:
                    data.append(None)
                else:
                    f = LegitLink.Transfer(dest.GetType(), self.GetType())
                    if f is None:
                        data.append(dest.Widget[dest.key])
                    elif callable(f):
                        data.append(f(dest.Widget[dest.key]))
                    else:
                        data.append(dest.Widget[dest.key][f])
            return data[0] if self.single else data
        return None

    # ----------------------------------------------------------
    def GetType(self):
        return self.aType

    def GetName(self):
        return ("--> %s <--" if self.recv else "<-- %s -->") % self.name
