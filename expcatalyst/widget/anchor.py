# -*- coding: utf-8 -*-


import wx
from .base import Base
from .link import LegitLink
from . import widget as Wi

__all__ = ["Anchor"]

# ======================================================= Anchor =======================================================
#   Anchors
#       aType     -  Anchor type,for defining legit links
#       key       -  Key for accessing (get/set) data associated with this widget
#       multiple  -  Whether this anchor can connect to multiple targets
#       send      -  Whether this anchor retrieve (IN) or send (OUT) associated data from/to its target
#       pos       -  The relative position of the anchor to the widget, use a negative value for automatic positioning
#       name      -  The tip displayed when being hovered
#
#       GetType   -
#       GetName   -
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


class Anchor(Base):
    def __init__(self, widget, aType, key, multiple, send, pos, name):
        super().__init__(w=6, h=6)
        self.Widget = widget
        self.Canvas = widget.Canvas
        self.aType = aType
        self.key = key
        self.multiple = multiple
        self.send = send
        self.posAllowed = pos
        self.name = name

        self.posAuto = len(self.posAllowed) > 1
        self.pos = self.posAllowed[0]
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

    # ----------------------------------------------
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

    # ----------------------------------------------
    def HandleMouse(self, evtType, evtPos):
        if evtType == wx.wxEVT_LEFT_DOWN:
            self.Canvas.TempLink = [self, None]
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
            elif isinstance(self.Canvas.Hovered, Wi.Widget):
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

    # ----------------------------------------------
    def EmptyTarget(self):
        if self.recv:
            for dest in self.connected.copy():
                dest.RemoveTarget(self)
        else:
            for dest in self.connected.copy():
                self.RemoveTarget(dest)

    def RemoveTarget(self, dest):  # self always send, dest always recv
        self.connected.remove(dest)
        dest.connected.remove(self)
        self.Canvas.RemoveLink(self, dest)
        dest.Widget.OnSetIncoming()

    def SetTarget(self, dest, sendEvent=True):  # self always send, dest always recv
        if DetectCircularReference(dest.Widget, self.Widget):  # Check the opposite send
            return self.Canvas.GetParent().SetStatus(self.Canvas.L["MSG_CIRCULAR_LINKAGE"], 1, 5)
        if dest in self.connected:
            return self.RemoveTarget(dest)
        if dest.single and dest.connected:
            dest.EmptyTarget()
        if self.single and self.connected:
            self.EmptyTarget()
        self.connected.append(dest)
        dest.connected.append(self)
        self.Canvas.AppendLink(self, dest)
        if sendEvent:
            dest.Widget.OnSetIncoming()

    # ------------------ Override ------------------
    def GetType(self):
        return self.aType

    def GetName(self):
        return ("In: " if self.recv else "Out: ") + self.name
