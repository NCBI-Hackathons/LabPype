# -*- coding: utf-8 -*-

import wx
import threading
import DynaUI as UI
from .. import utility as Ut

MOCK_RECT = wx.Rect(0, 0, 0, 0)


# ======================================================= Canvas =======================================================
class Canvas(UI.BaseControl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.WANTS_CHARS, font=parent.R["FONT_CANVAS"], bg="B", fg="B", fpsLimit=60)
        self.F = parent
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.NewAnimation("LOCATE", 50, self.ToggleSelect, (), False)
        self.NewTimer("_WIDGET_UPDATE_", lambda: self.ReDraw() if self.widgetRunning else None)
        self.NewTimer("_HIDDEN_RESIZE_", self.ReSizeHidden)
        self.NewTimer("_HIDDEN_REDRAW_", self.ReDrawHidden)
        self.NewTimer("_HIDDEN_FORCE_DRAW_", self.ReDrawHidden)
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

        self.widgetRunning = 0
        self.hiddenBitmap = None
        self.hiddenImage = None

        self.Lock = threading.RLock()
        self.Widget = []
        self.Link = {}

        self.StartTimer("_WIDGET_UPDATE_", 500, wx.TIMER_CONTINUOUS)
        self.ReSizeHidden()

    def OnSize(self, evt):
        w, h = evt.GetSize()
        self.borderPoints = (0, 0), (0, h - 1), (w - 1, h - 1), (w - 1, 0), (0, 0)
        self.StartTimer("_HIDDEN_RESIZE_", 100, wx.TIMER_ONE_SHOT)
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
            return self.F.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_TOO_MANY_WIDGETS")
        if W.UNIQUE and W.__INSTANCE__:
            return self.F.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_SINGLETON_EXISTS")
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
        self.ReDraw()

    def DeleteSelected(self):
        if not self.SelectedWidget and not self.SelectedLink:
            return
        self.Hovered = None
        self.Clicked = None
        if self.SelectedLink:
            self.SelectedLink.Disconnect()
            self.SelectedLink = None
        else:
            while self.SelectedWidget:
                w = self.SelectedWidget.pop()
                self.Widget.remove(w)
                w.Destroy()
        self.ReDraw()

    def WidgetRunning(self, running):
        if running:
            self.widgetRunning += 1
        else:
            self.widgetRunning -= 1

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

    def UpdateSelection(self):
        for w in self.Widget:
            self.OnSelect(w, self.SelectionRect.Intersects(w.rect))

    def OnSelect(self, w, selected=True):
        if selected and w not in self.SelectedWidget:
            self.SelectedWidget.append(w)
        elif not selected and w in self.SelectedWidget:
            self.SelectedWidget.remove(w)

    def ToggleSelect(self, w):
        if w in self.SelectedWidget:
            self.SelectedWidget.remove(w)
        else:
            self.SelectedWidget.append(w)

    def SelectAll(self):
        self.SelectedLink = None
        self.SelectedWidget = self.Widget[::]
        self.ReDraw()

    def SelectNone(self):
        self.SelectedLink = None
        self.SelectedWidget = []
        self.ReDraw()

    # ----------------------------------------------
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
                self.SetSelectionArea(evtPos, 0)
                self.SelectAll() if evtType == wx.wxEVT_LEFT_DCLICK else self.SelectNone()
            else:
                if self.Clicked not in self.SelectedWidget:
                    self.SelectNone()
                if self.Clicked.__TYPE__ == "LINK":
                    self.SelectedLink = self.Clicked
        if self.Clicked:
            if self.Clicked.__TYPE__ == "WIDGET":
                if evtType == wx.wxEVT_LEFT_DOWN:
                    self.OnSelect(self.Clicked)
                elif evtType == wx.wxEVT_LEFT_DCLICK:
                    if self.Clicked.DIALOG and not evtShift:
                        self.Clicked.OnActivation()
                    else:
                        self.Clicked.OnAbort()
                        self.Clicked.OnBegin()
                elif evtType == wx.wxEVT_MOTION:
                    for w in self.SelectedWidget:
                        w.RePosition(*(evtPos - self.leftPos))
            elif self.Clicked.__TYPE__ == "ANCHOR":
                self.Clicked.HandleMouse(evtType, evtPos)
        elif evtType == wx.wxEVT_MOTION:
            self.SetSelectionArea(-1, evtPos)
            self.UpdateSelection()
        if evtType == wx.wxEVT_LEFT_UP:
            if self.HasCapture(): self.ReleaseMouse()
            self.leftPos = None
            self.Clicked = None
            self.SetSelectionArea(0, 0)
            for w in self.SelectedWidget:
                w.SavePosition()

    def HandleMouseMiddle(self, evtType, evtPos):
        if self.Hovered and self.Hovered.__TYPE__ == "WIDGET":
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
            self.rightPos = evtPos
            self.SelectedLink = None
            if self.Hovered and self.Hovered.__TYPE__ == "WIDGET":
                self.OnSelect(self.Hovered, not self.Hovered in self.SelectedWidget)
        elif evtType == wx.wxEVT_RIGHT_UP:
            self.rightPos = None

    def HandleMouseMotion(self, evtPos):
        newObj = self.GetHovered(evtPos)
        if self.Hovered != newObj:
            self.Hovered = newObj
            if hasattr(newObj, "__TYPE__"):
                self.F.SetStatus(newObj.GetName())
            else:
                self.F.SetStatus("")
            return True

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
            return self.Link.get(self.hiddenImage.GetRed(*pos) << 16 |
                                 self.hiddenImage.GetGreen(*pos) << 8 |
                                 self.hiddenImage.GetBlue(*pos))

    # ----------------------------------------------
    def DrawLink(self, gc, selected):
        x1, y1, x2, y2, c1, c2 = selected.GetXY()
        self.DrawLink2(gc, x1, y1, x2, y2, c1, c2, self.R["PEN_CONNECTION_SELECTION1"])
        self.DrawLink2(gc, x1, y1, x2, y2, c1, c2, self.R["PEN_CONNECTION_SELECTION2"])

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)
        dc.nameTexts = []
        dc.nameXYs = []
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
        if self.SelectedLink:
            self.DrawLink(gc, self.SelectedLink)
        elif self.SelectedWidget:
            dc.DrawRectangleList([w.rect for w in self.SelectedWidget])

        # Layer 2 - Hover
        if self.Hovered:
            if self.Hovered.__TYPE__ == "WIDGET":
                dc.DrawRectangle(self.Hovered.rect)
            elif self.Hovered.__TYPE__ == "ANCHOR":
                dc.DrawRectangle(self.Hovered.rect)
            elif self.Hovered.__TYPE__ == "LINK" and self.Hovered != self.SelectedLink:
                self.DrawLink(gc, self.Hovered)

        # Layer 3 - Widget
        dc.SetPen(wx.TRANSPARENT_PEN)
        for w in self.Widget:
            w.Draw(dc)

        # Layer 4 - Linkage
        path = gc.CreatePath()
        for link in self.Link.values():
            self.DrawLink1(path, *link.GetXY())
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

        dc.DrawTextList(dc.nameTexts, dc.nameXYs)

        # Layer 6 - Border
        dc.SetPen(self.R["PEN_EDGE_B"])
        dc.DrawLines(self.borderPoints)

        # Finish
        self.StartTimer("_HIDDEN_REDRAW_", 100, wx.TIMER_ONE_SHOT)
        if not self.Timers["_HIDDEN_FORCE_DRAW_"].IsRunning():
            self.StartTimer("_HIDDEN_FORCE_DRAW_", 1000, wx.TIMER_ONE_SHOT)

    def ReSizeHidden(self):
        w, h = self.GetSize()
        self.hiddenBitmap = wx.Bitmap(w, h)
        self.hiddenImage = self.hiddenBitmap.ConvertToImage()

    def ReDrawHidden(self):
        self.StopTimer("_HIDDEN_REDRAW_")
        self.StopTimer("_HIDDEN_FORCE_DRAW_")
        mdc = wx.MemoryDC()
        mdc.SelectObject(self.hiddenBitmap)
        mdc.SetBackground(wx.BLACK_BRUSH)
        mdc.Clear()
        mgc = wx.GraphicsContext.Create(mdc)
        mgc.SetAntialiasMode(wx.ANTIALIAS_NONE)
        for link in self.Link.values():
            self.DrawLink2(mgc, *link.GetXY(), link.pen)
        mdc.SelectObject(wx.NullBitmap)
        self.hiddenImage = self.hiddenBitmap.ConvertToImage()


# ----------------------------------------------
def DrawCurve(path, x1, y1, x2, y2, c1, c2):
    path.MoveToPoint(x1, y1)
    path.AddCurveToPoint(c1, y1, c2, y2, x2, y2)


def DrawStraight(path, x1, y1, x2, y2, c1, c2):
    path.MoveToPoint(x1, y1)
    path.AddLineToPoint(x1 + 8, y1)
    path.AddLineToPoint(x2 - 8, y2)
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
