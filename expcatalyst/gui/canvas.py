# -*- coding: utf-8 -*-


import wx
import time
import DynaUI as UI
from .. import utility as Ut

from ..widget import Widget
from ..widget import Anchor

MOCK_RECT = wx.Rect(0, 0, 0, 0)


# ======================================================= Canvas =======================================================
class Canvas(UI.BaseControl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.WANTS_CHARS, font=parent.R["FONT_CANVAS"], bg="B", fg="B", fpsLimit=60)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.NewAnimation("LOCATE", 50, self.ToggleSelect, (), False)  # TODO
        self.NewTimer("__", self.ReDraw)
        self.NewTimer("___", self.ReDrawHidden)
        self.SetStatus = parent.SetStatus
        if self.S["TOGGLE_CURV"]:
            self.DrawLink1 = DrawCurve
            self.DrawLink2 = DrawCurve2
        else:
            self.DrawLink1 = DrawStraight
            self.DrawLink2 = DrawStraight2

        self.Hovered = None
        self.Clicked = None
        self.leftPos = None
        self.middlePos = None
        self.rightPos = None
        self.SelectionArea = [0, 0]
        self.SelectionRect = MOCK_RECT
        self.SelectedWidget = []
        self.SelectedLink = None
        self.TempLink = None

        self.timeLastDraw = 0
        self.timeLastBlink = 0
        self.colorLastBlink = 0
        self.widgetBlinking = 0
        self.hiddenBitmap = None
        self.hiddenImage = None

        self.Widget = []
        self.Link = {}

    def OnSize(self, evt):
        w, h = evt.GetSize()
        self.hiddenBitmap = wx.Bitmap(w, h)
        self.hiddenImage = self.hiddenBitmap.ConvertToImage()
        self.borderPoints = (0, 0), (0, h - 1), (w - 1, h - 1), (w - 1, 0), (0, 0)
        evt.Skip()

    def ToggleLinkType(self):
        self.S["TOGGLE_CURV"] = not self.S["TOGGLE_CURV"]
        if self.S["TOGGLE_CURV"]:
            self.DrawLink1 = DrawCurve
            self.DrawLink2 = DrawCurve2
        else:
            self.DrawLink1 = DrawStraight
            self.DrawLink2 = DrawStraight2
        self.ReDraw()

    # ----------------------------------------------
    def Align(self, f):
        if self.SelectedWidget:
            for index, pos in enumerate(f([w.GetPosition() for w in self.SelectedWidget])):
                self.SelectedWidget[index].SetPosition(int(pos[0]), int(pos[1]))
            self.ReDraw()

    def Distribute(self, f):
        if self.SelectedWidget:
            self.SelectedWidget.sort(key=lambda k: k.GetPosition()[f == Ut.DistributeV])
            for index, pos in enumerate(f([i.GetPosition() for i in self.SelectedWidget])):
                self.SelectedWidget[index].SetPosition(int(pos[0]), int(pos[1]))
            self.ReDraw()

    def AlterLayer(self, d):
        for w, oldIndex in sorted([(w, self.Widget.index(w)) for w in self.SelectedWidget], key=lambda x: x[1], reverse=d in ("D", "B")):
            self.Widget.remove(w)
            if d == "T":
                self.Widget.append(w)
            elif d == "U":
                self.Widget.insert(oldIndex + 1, w)
            elif d == "D":
                self.Widget.insert(max(oldIndex - 1, 0), w)
            elif d == "B":
                self.Widget.insert(0, w)
            self.ReDraw()

    # ----------------------------------------------
    def AddWidget(self, W, pos=(20, 20)):
        if len(self.Widget) > 255:
            self.GetParent().OnDialog("MSG_TOO_MANY_WIDGETS", "SIMPLE_TEXT", self.L["GENERAL_HEAD_FAIL"], self.L["MSG_TOO_MANY_WIDGETS"])
            return
        if isinstance(W.SINGLETON, W):
            self.GetParent().OnDialog("MSG_SINGLETON_EXISTS", "SIMPLE_TEXT", self.L["GENERAL_HEAD_FAIL"], self.L["MSG_SINGLETON_EXISTS"])
            return
        w = W(self)
        w.SetPosition(*pos)
        self.Widget.append(w)
        self.ReDraw()
        return w

    def ClearWidget(self):
        self.OnCaptureLost(None)
        self.SelectedWidget = []
        self.SelectedLink = None
        while self.Widget:
            self.Widget.pop().Destroy()
        self.Link = {}
        self.ReDraw()

    def DeleteSelected(self):
        if not self.SelectedWidget and not self.SelectedLink:
            return
        self.leftPos = None
        self.Hovered = None
        self.Clicked = None
        if self.SelectedLink:
            self.SelectedLink[0].RemoveTarget(self.SelectedLink[1], True)
            self.SelectedLink = None
        else:
            while self.SelectedWidget:
                w = self.SelectedWidget.pop()
                self.Widget.remove(w)
                w.Destroy()
        self.ReDraw()

    def WidgetRunning(self, running):
        if running:
            self.widgetBlinking += 1
            if self.widgetBlinking == 1:
                self.StartTimer("__", 100, wx.TIMER_CONTINUOUS)
        else:
            self.widgetBlinking -= 1
            if self.widgetBlinking == 0:
                self.StopTimer("__")

    # ----------------------------------------------
    def AppendLink(self, source, target):
        rgb = source.Id << 12 | target.Id
        r = (rgb >> 16) & 0b11111111
        g = (rgb >> 8) & 0b11111111
        b = rgb & 0b11111111
        pen = wx.Pen(wx.Colour(r, g, b), 11)
        pen.SetCap(wx.CAP_BUTT)
        self.Link[rgb] = (source, target, pen)

    def RemoveLink(self, source, target):
        del self.Link[source.Id << 12 | target.Id]

    # ----------------------------------------------
    def SetSelectionArea(self, pos1=-1, pos2=-1):
        if pos1 != -1:
            self.SelectionArea[0] = pos1
        if pos2 != -1:
            self.SelectionArea[1] = pos2
        if all(self.SelectionArea):
            x1, y1 = self.SelectionArea[0]
            x2, y2 = self.SelectionArea[1]
            self.SelectionRect = wx.Rect(min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2))
        else:
            self.SelectionRect = MOCK_RECT

    def ClearSelectionArea(self):
        self.SelectionArea = [0, 0]
        self.SelectionRect = MOCK_RECT

    def UpdateSelection(self):
        for w in self.Widget:
            self.OnSelect(w, self.SelectionRect.Intersects(w.rect))

    def OnSelect(self, w, selected=True):
        if selected and w not in self.SelectedWidget:
            self.SelectedWidget.append(w)
        elif not selected and w in self.SelectedWidget:
            self.SelectedWidget.remove(w)

    def ToggleSelect(self, w):  # TODO -
        if w in self.SelectedWidget:
            self.SelectedWidget.remove(w)
        else:
            self.SelectedWidget.append(w)

    def SelectAll(self, evt=None):
        self.SelectedWidget = self.Widget[::]
        self.ReDraw()

    def SelectNone(self):
        self.SelectedWidget = []
        self.ReDraw()

    # ----------------------------------------------
    def GetHovered(self, pos):
        if self.S["TOGGLE_ANCR"]:
            for w in reversed(self.Widget):
                for c in w.Anchors:
                    if c.Contains(pos):
                        return c
                if w.Contains(pos):
                    return w
        else:
            for w in reversed(self.Widget):
                if w.Contains(pos):
                    return w
        if 0 <= pos[0] < self.hiddenImage.GetWidth() and 0 <= pos[1] < self.hiddenImage.GetHeight():
            r = self.hiddenImage.GetRed(*pos)
            g = self.hiddenImage.GetGreen(*pos)
            b = self.hiddenImage.GetBlue(*pos)
            return self.Link.get(r << 16 | g << 8 | b)

    def OnCaptureLost(self, evt):
        self.Hovered = None
        self.Clicked = None
        self.leftPos = None
        self.middlePos = None
        self.rightPos = None
        self.SelectionArea = [0, 0]
        self.SelectionRect = MOCK_RECT
        self.TempLink = None
        for w in self.Widget:
            w.SavePosition()
        self.SetCursor(self.R["CURSOR_NORMAL"])
        self.ReDraw()

    def OnMouse(self, evt):
        evtType = evt.GetEventType()
        evtPos = evt.GetPosition()
        evtShift = evt.ShiftDown()
        # evtControl = evt.ControlDown()
        if self.leftPos or evtType == wx.wxEVT_LEFT_DOWN or evtType == wx.wxEVT_LEFT_DCLICK:
            self.HandleMouseLeft(evtType, evtPos, evtShift)
            self.ReDraw()
        elif self.middlePos or evtType == wx.wxEVT_MIDDLE_DOWN or evtType == wx.wxEVT_MIDDLE_DCLICK:
            self.HandleMouseMiddle(evtType, evtPos)
            self.ReDraw()
        elif self.rightPos or evtType == wx.wxEVT_RIGHT_DOWN or evtType == wx.wxEVT_RIGHT_DCLICK:
            self.HandleMouseRight(evtType, evtPos)
            self.ReDraw()
        else:
            if self.HandleMouseMotion(evtPos):
                self.ReDraw()

    def HandleMouseLeft(self, evtType, evtPos, evtShift):
        if evtType == wx.wxEVT_LEFT_DOWN or evtType == wx.wxEVT_LEFT_DCLICK:
            if not self.HasCapture(): self.CaptureMouse()
            if not self.HasFocus(): self.SetFocus()
            self.leftPos = evtPos
            self.Clicked = self.Hovered
            if self.Clicked is None:
                self.SetSelectionArea(evtPos, evtPos)
                self.SelectAll() if evtType == wx.wxEVT_LEFT_DCLICK else self.SelectNone()
            elif self.Clicked and self.Clicked not in self.SelectedWidget:
                self.SelectNone()
            if isinstance(self.Clicked, tuple):
                self.SelectedLink = self.Clicked
            else:
                self.SelectedLink = None
        if self.Clicked:
            if isinstance(self.Clicked, Widget):
                if evtType == wx.wxEVT_LEFT_DOWN:
                    self.OnSelect(self.Clicked)
                elif evtType == wx.wxEVT_LEFT_DCLICK:
                    if evtShift:
                        self.Clicked.OnStart()
                    elif self.Clicked.DIALOG:
                        self.Clicked.OnActivation()
                    else:
                        self.Clicked.OnStart()
                elif evtType == wx.wxEVT_MOTION:
                    for w in self.SelectedWidget:
                        w.RePosition(*(evtPos - self.leftPos))
            elif isinstance(self.Clicked, Anchor):
                self.Clicked.HandleMouse(evtType, evtPos)
        elif evtType == wx.wxEVT_MOTION:
            self.SetSelectionArea(pos2=evtPos)
            self.UpdateSelection()
        if evtType == wx.wxEVT_LEFT_UP:
            if self.HasCapture(): self.ReleaseMouse()
            self.leftPos = None
            self.SetSelectionArea(0, 0)
            self.Clicked = None
            for w in self.SelectedWidget:
                w.SavePosition()

    def HandleMouseMiddle(self, evtType, evtPos):
        if isinstance(self.Hovered, Widget):
            if evtType == wx.wxEVT_MIDDLE_DOWN:
                self.OnSelect(self.Hovered)
                for w in self.Hovered.GetLinkedWidget():
                    self.OnSelect(w)
        else:
            if evtType == wx.wxEVT_MIDDLE_DOWN:
                if not self.HasCapture(): self.CaptureMouse()
                self.middlePos = evtPos
                self.SetCursor(self.R["CURSOR_MOVING"])
            elif evtType == wx.wxEVT_MIDDLE_UP:
                if self.HasCapture(): self.ReleaseMouse()
                self.middlePos = None
                self.SetCursor(self.R["CURSOR_NORMAL"])
                for w in self.Widget:
                    w.SavePosition()
            elif evtType == wx.wxEVT_MOTION:
                for w in self.Widget:
                    w.RePosition(*(evtPos - self.middlePos))

    def HandleMouseRight(self, evtType, evtPos):
        if evtType == wx.wxEVT_RIGHT_DOWN or evtType == wx.wxEVT_RIGHT_DCLICK:
            self.SelectedLink = None
            if isinstance(self.Hovered, Widget):
                self.OnSelect(self.Hovered, not self.Hovered in self.SelectedWidget)
            self.rightPos = evtPos
        elif evtType == wx.wxEVT_RIGHT_UP:
            self.rightPos = None

    def HandleMouseMotion(self, evtPos):
        newObj = self.GetHovered(evtPos)
        if self.Hovered != newObj:
            self.Hovered = newObj
            if isinstance(newObj, Widget):
                self.SetStatus(newObj.name)
            elif isinstance(newObj, Anchor):
                self.SetStatus(newObj.GetName())
            elif isinstance(newObj, tuple):
                self.SetStatus("[%s].[%s] --> [%s].[%s]" % (newObj[0].Widget.NAME, newObj[0].name, newObj[1].Widget.NAME, newObj[1].name), 1)
            else:
                self.SetStatus("")
            return True

    # ----------------------------------------------
    def DrawLink(self, gc, selected):
        x1, y1 = (selected[0].x + 3, selected[0].y + 3)
        x2, y2 = (selected[1].x + 3, selected[1].y + 3)
        c = (x1 + x2) / 2
        c1 = max(c, x1 + 32)
        c2 = min(c, x2 - 32)
        self.DrawLink2(gc, x1, y1, x2, y2, c1, c2, self.R["PEN_CONNECTION_SELECTION1"])
        self.DrawLink2(gc, x1, y1, x2, y2, c1, c2, self.R["PEN_CONNECTION_SELECTION2"])

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)
        dc.nameTexts = []
        dc.namePoints = []
        dc.anchorOutgoing = []
        dc.anchorIdleR = []
        dc.anchorPassR = []
        dc.anchorFailR = []
        dc.anchorIdleE = []
        dc.anchorPassE = []
        dc.anchorFailE = []

        # Layer 1 - SelectedWidget
        dc.SetPen(self.R["PEN_SELECTION"])
        dc.SetBrush(self.R["BRUSH_SELECTION"])
        dc.DrawRectangle(self.SelectionRect)
        dc.DrawRectangleList([w.rect for w in self.SelectedWidget])
        if self.SelectedLink:
            self.DrawLink(gc, self.SelectedLink)

        # Layer 2 - Hover
        if isinstance(self.Hovered, Widget):
            dc.DrawRectangle(self.Hovered.rect)
        elif isinstance(self.Hovered, Anchor):
            dc.DrawRectangle(self.Hovered.rect)
        elif isinstance(self.Hovered, tuple) and self.Hovered != self.SelectedLink:
            self.DrawLink(gc, self.Hovered)

        # Layer 3 - Widget
        dc.SetPen(wx.TRANSPARENT_PEN)
        for w in self.Widget:
            w.Draw(dc)

        # Layer 4 - Linkage
        path = gc.CreatePath()
        for link in self.Link.values():
            x1, y1 = link[0].x + 3, link[0].y + 3
            x2, y2 = link[1].x + 3, link[1].y + 3
            c = (x1 + x2) / 2
            c1 = max(c, x1 + 32)
            c2 = min(c, x2 - 32)
            self.DrawLink1(path, x1, y1, x2, y2, c1, c2)
        if self.TempLink and self.TempLink[1]:
            if self.TempLink[3]:
                x1, y1 = self.TempLink[0]
                x2, y2 = self.TempLink[1]
            else:
                x2, y2 = self.TempLink[0]
                x1, y1 = self.TempLink[1]
            c = (x1 + x2) / 2
            c1 = max(c, x1 + 32)
            c2 = min(c, x2 - 32)
            self.DrawLink1(path, x1, y1, x2, y2, c1, c2)
            path.AddCircle(*self.TempLink[2], 1)
            path.AddCircle(*self.TempLink[2], 6)
        gc.SetPen(self.R["PEN_CONNECTION"])
        gc.StrokePath(path)

        # Layer 5 - Anchor & Name
        dc.SetBrush(self.R["BRUSH_ANCHOR_RECV"])
        dc.DrawRectangleList(dc.anchorIdleR)
        dc.DrawEllipseList(dc.anchorIdleE)
        dc.SetBrush(self.R["BRUSH_ANCHOR_SEND"])
        dc.DrawRectangleList(dc.anchorOutgoing)
        dc.SetBrush(self.R["BRUSH_ANCHOR_PASS"])
        dc.DrawRectangleList(dc.anchorPassR)
        dc.DrawEllipseList(dc.anchorPassE)
        dc.SetBrush(self.R["BRUSH_ANCHOR_FAIL"])
        dc.DrawRectangleList(dc.anchorFailR)
        dc.DrawEllipseList(dc.anchorFailE)

        dc.DrawTextList(dc.nameTexts, dc.namePoints)

        # Layer 6 - Border
        dc.SetPen(self.R["PEN_EDGE_B"])
        dc.DrawLines(self.borderPoints)

        # Finish
        self.timeLastDraw = time.time()
        if self.timeLastDraw > self.timeLastBlink + 0.2:
            self.timeLastBlink = self.timeLastDraw
            self.colorLastBlink = not self.colorLastBlink

        self.StartTimer("___", 100, wx.TIMER_ONE_SHOT)

    def ReDrawHidden(self):
        mdc = wx.MemoryDC()
        mdc.SelectObject(self.hiddenBitmap)
        mdc.SetBackground(wx.BLACK_BRUSH)
        mdc.Clear()
        mgc = wx.GraphicsContext.Create(mdc)
        mgc.SetAntialiasMode(wx.ANTIALIAS_NONE)
        for link in self.Link.values():
            x1, y1 = link[0].x + 3, link[0].y + 3
            x2, y2 = link[1].x + 3, link[1].y + 3
            c = (x1 + x2) / 2
            c1 = max(c, x1 + 32)
            c2 = min(c, x2 - 32)
            self.DrawLink2(mgc, x1, y1, x2, y2, c1, c2, link[2])
        mdc.SelectObject(wx.NullBitmap)
        self.hiddenImage = self.hiddenBitmap.ConvertToImage()


# ----------------------------------------------
def DrawCurve(path, x1, y1, x2, y2, c1, c2):
    path.MoveToPoint(x1, y1)
    path.AddCurveToPoint(c1, y1, c2, y2, x2, y2)


def DrawStraight(path, x1, y1, x2, y2, c1, c2):
    path.MoveToPoint(x1, y1)
    path.AddLineToPoint(x2, y2)


def DrawCurve2(gc, x1, y1, x2, y2, c1, c2, pen):
    gc.SetPen(pen)
    path = gc.CreatePath()
    DrawCurve(path, x1, y1, x2, y2, c1, c2)
    gc.StrokePath(path)


def DrawStraight2(gc, x1, y1, x2, y2, c1, c2, pen):
    gc.SetPen(pen)
    path = gc.CreatePath()
    DrawStraight(path, x1, y1, x2, y2, c1, c2)
    gc.StrokePath(path)
