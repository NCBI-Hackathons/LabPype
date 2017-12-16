# -*- coding: utf-8 -*-

import wx
from .base import Base
from .link import LegitLink

__all__ = ["Anchor"]

# ======================================================= Anchor =======================================================
#   aType     -  Anchor type, for defining legit links
#   key       -  Key for accessing (get/set) data associated with this widget
#   multiple  -  Whether this anchor supports multiple connections
#   send      -  Whether this anchor retrieve (IN) or send (OUT) associated data from/to its target
#   pos       -  The relative position of the anchor to the widget, support multiple positions
#   name      -  Default text displayed when being hovered
#
#   GetType   -  By default return aType. Override for flexibility
#   GetName   -  How canvas display the name of this anchor
# ======================================================= Anchor =======================================================
ANCHOR_STATE_IDLE = 1 << 0
ANCHOR_STATE_PASS = 1 << 1
ANCHOR_STATE_FAIL = 1 << 2


def DetectCircularReference(Incoming, Outgoing, visited=None):
    if visited is None: visited = []
    for a in Incoming.Outgoing:
        for dest in a.connected:
            if dest.Widget.Id not in visited:
                visited.append(dest.Widget.Id)
                if dest.Widget == Outgoing or DetectCircularReference(dest.Widget, Outgoing, visited):
                    return True


NEAREST_POS = {
    -3: (-3, -2, +3, +0),
    -2: (-2, -3, +0, +3),
    -1: (-1, +0, -3, +2),
    +0: (+0, -1, +2, -3),
    +1: (+1, +2, -1, +4),
    +2: (+2, +1, +4, -1),
    +3: (+3, +4, +1, -2),
    +4: (+4, +3, -2, +1), }
POS_MAP = {
    -3: "L", -2: "T", -1: "T", +0: "R",
    +1: "R", +2: "B", +3: "B", +4: "L", }
POS_TABLE = {}
for binPos in range(1, 16):
    POS_TABLE[binPos] = {}
    allowed = set()
    if 0b1000 & binPos:  # L
        allowed.update((-3, +4))
    if 0b0100 & binPos:  # T
        allowed.update((-2, -1))
    if 0b0010 & binPos:  # R
        allowed.update((+0, +1))
    if 0b0001 & binPos:  # B
        allowed.update((+2, +3))
    for index in NEAREST_POS:
        POS_TABLE[binPos][index] = POS_MAP[[i for i in NEAREST_POS[index] if i in allowed][0]]


class Anchor(Base):
    def __init__(self, widget, aType, key, multiple, send, pos, name):
        super().__init__(w=6, h=6)
        self.Widget = widget
        self.Canvas = widget.Canvas
        self.aType = aType
        self.key = key
        self.multiple = multiple
        self.send = send
        self.name = name

        self.posAllowed = pos
        self.posTable = POS_TABLE[(0b1000 if "L" in pos else 0) | (0b0100 if "T" in pos else 0) | (0b0010 if "R" in pos else 0) | (0b0001 if "B" in pos else 0)]
        self.pos = pos[0]

        self.single = not multiple
        self.recv = not send
        self.rect.SetSize((18, 18))
        self.connected = []
        self.pointing = None
        self.leftPos = None
        self.state = ANCHOR_STATE_IDLE
        self.Draw = (self.DrawRectangle if self.multiple else self.DrawEllipse) if self.recv else self.DrawOutgoing

    def SetState(self, state):
        self.state = state

    def NewPosition(self, x, y):
        self.x = x
        self.y = y
        self.rect.SetPosition((x - 6, y - 6))

    # ----------------------------------------------------------
    def DrawOutgoing(self, dc):
        if self.state == ANCHOR_STATE_IDLE:
            dc.anchorOutgoing.append((self.x, self.y, 6, 6))
        elif self.state == ANCHOR_STATE_PASS:
            dc.anchorPassR.append((self.x, self.y, 6, 6))
        elif self.state == ANCHOR_STATE_FAIL:
            dc.anchorFailR.append((self.x, self.y, 6, 6))

    def DrawRectangle(self, dc):
        if self.state == ANCHOR_STATE_IDLE:
            dc.anchorIdleR.append((self.x, self.y, 6, 6))
        elif self.state == ANCHOR_STATE_PASS:
            dc.anchorPassR.append((self.x, self.y, 6, 6))
        elif self.state == ANCHOR_STATE_FAIL:
            dc.anchorFailR.append((self.x, self.y, 6, 6))

    def DrawEllipse(self, dc):
        if self.state == ANCHOR_STATE_IDLE:
            dc.anchorIdleE.append((self.x, self.y, 6, 6))
        elif self.state == ANCHOR_STATE_PASS:
            dc.anchorPassE.append((self.x, self.y, 6, 6))
        elif self.state == ANCHOR_STATE_FAIL:
            dc.anchorFailE.append((self.x, self.y, 6, 6))

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
            elif hasattr(self.Canvas.Hovered, "__INITIALIZED__"):
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
    def EmptyTarget(self, onAlter):
        if self.recv:
            for dest in self.connected.copy():
                dest.RemoveTarget(self, False)
            if onAlter:
                self.Widget.OnAlter()
        else:
            for dest in self.connected.copy():
                self.RemoveTarget(dest, onAlter)

    def RemoveTarget(self, dest, onAlter):  # self always send, dest always recv
        self.connected.remove(dest)
        dest.connected.remove(self)
        self.Canvas.RemoveLink(self, dest)
        if onAlter:
            dest.Widget.OnAlter()

    def SetTarget(self, dest, onAlter=True):  # self always send, dest always recv
        if DetectCircularReference(dest.Widget, self.Widget):  # Check the opposite send
            return self.Canvas.F.SetStatus(self.Canvas.L["MSG_CIRCULAR_LINKAGE"], 1, 5)
        if dest in self.connected:
            return self.RemoveTarget(dest, True)
        if dest.single and dest.connected:
            dest.EmptyTarget(False)
        if self.single and self.connected:
            self.EmptyTarget(True)
        self.connected.append(dest)
        dest.connected.append(self)
        self.Canvas.AppendLink(self, dest)
        if onAlter:
            dest.Widget.OnAlter()

    def Retrieve(self):
        if self.connected:
            data = [LegitLink.Transfer(dest.GetType(), self.GetType())(dest.Widget[dest.key]) for dest in self.connected]
            return data[0] if self.single else data
        return None

    # ----------------------------------------------------------
    def GetType(self):
        return self.aType

    def GetName(self):
        return ("--> %s <--" if self.recv else "<-- %s -->") % self.name
