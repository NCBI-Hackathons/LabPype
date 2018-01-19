# -*- coding: utf-8 -*-

import wx
import DynaUI as UI
from .field import *

__all__ = ["Dialog", "DisableCanvas", "FreezeAndThaw"]

SIZE_BTN = wx.Size(20, 20)
SF_HEAD = wx.SizerFlags().Expand().Border(wx.TOP, 2)
SF_MAIN = wx.SizerFlags().Expand().Border(wx.ALL, 2)
SF_SASH = wx.SizerFlags().Expand().Border(wx.BOTTOM, 6)

DisableCanvas = lambda func: lambda self: (self.DisableCanvas(), func(self), self.EnableCanvas())
FreezeAndThaw = lambda func: lambda self: (self.Freeze(), func(self), self.Thaw())


# ==================================================== DetachedHead ====================================================
class DetachedHead(UI.BaseHead):
    def __init__(self, parent, help):
        super().__init__(parent, buttons=False)
        size = UI.SETTINGS["DLG_HEAD_BTN"]
        Sizer = self.GetSizer()
        Sizer.Insert(1, UI.ToolNormal(self, size=size, pics=self.R["DIALOG_LOCA"], func=self.Frame.Main.Locate), self.SizerFlags)
        Sizer.Insert(1, UI.ToolNormal(self, size=size, pics=self.R["DIALOG_ATCH"], func=self.Frame.Main.Attach), self.SizerFlags)
        if help:
            Sizer.Insert(0, UI.ToolNormal(self, size=size, pics=self.R["AP_HELP"], func=(self.GetGrandParent().OnSimpleDialog, "GENERAL_HEAD_HELP", help)), self.SizerFlags)
            Sizer.Insert(0, 3, 0)
            self.SetTagOffset(self.TagOffset[0] + size[0], self.TagOffset[1])

    def OnMouse(self, evt):  # TODO Multiple screen see wx.Display
        if evt.GetEventType() == wx.wxEVT_MOTION and self.lastMousePos:
            newPos = self.lastFramePos - self.lastMousePos + self.Frame.ClientToScreen(evt.GetPosition())
            size = self.Frame.GetSize()
            UI.EnsureWindowInScreen(newPos, size, 12)
            l, t = newPos
            b = t + size[1]
            r = l + size[0]
            closestH = closestV = UI.SETTINGS["DLG_HEAD"] // 2
            for frame in wx.GetTopLevelWindows():
                if isinstance(frame, UI.BaseDialog) and frame != self.Frame and frame.IsShown():
                    _l, _t = frame.GetPosition()
                    _b = _t + frame.GetSize()[1]
                    _r = _l + frame.GetSize()[0]
                    if _l <= l < _r or _l < r <= _r:
                        d = abs(t - _b)
                        if d < closestV:
                            closestV = d
                            newPos[1] = _b
                        d = abs(b - _t)
                        if d < closestV:
                            closestV = d
                            newPos[1] = _t - size[1]
                        d = abs(t - _t)
                        if d < closestV:
                            closestV = d
                            newPos[1] = _t
                        d = abs(b - _b)
                        if d < closestV:
                            closestV = d
                            newPos[1] = _b - size[1]
                    if _t <= t < _b or _t < b <= _b:
                        d = abs(l - _r)
                        if d < closestH:
                            closestH = d
                            newPos[0] = _r
                        d = abs(r - _l)
                        if d < closestH:
                            closestH = d
                            newPos[0] = _l - size[0]
                        d = abs(l - _l)
                        if d < closestH:
                            closestH = d
                            newPos[0] = _l
                        d = abs(r - _r)
                        if d < closestH:
                            closestH = d
                            newPos[0] = _r - size[0]
            self.Frame.SetPosition(newPos)
        else:
            super().OnMouse(evt)


# ==================================================== AttachedHead ====================================================
class AttachedHead(UI.Button):
    def __init__(self, parent, tag, pic, func):
        super().__init__(parent=parent, size=(-1, 20), tag=(tag, "L", 20), pic=(pic, "L"), func=func, fg="B", edge="D", res="R")
        Sizer = wx.BoxSizer(wx.HORIZONTAL)
        Sizer.AddMany((
            (4, 4, 1),
            (UI.ToolNormal(self, size=SIZE_BTN, pics=self.R["DIALOG_DTCH"], edge=("", "TB"), func=func[1].Detach)),
            (UI.ToolNormal(self, size=SIZE_BTN, pics=self.R["DIALOG_LOCA"], edge=("", "TB"), func=func[1].Locate)),
            (UI.ToolNormal(self, size=SIZE_BTN, pics=self.R["AP_EXIT"], edge=("", "RTB"), func=func[1].OnClose, res="R"))
        ))
        self.SetSizer(Sizer)


# ==================================================== DialogMaker =====================================================
def MakeWidgetDialog(widget):
    Frame = UI.BaseDialog(parent=widget.Canvas.F,
                          title=widget.NAME,
                          style=wx.FRAME_FLOAT_ON_PARENT,
                          main=(widget.DIALOG, {"widget": widget}),
                          head=(DetachedHead, {"help": widget.DIALOG.HELP}),
                          grip={"minSize": widget.DIALOG.MIN_SIZE}, )
    x, y = widget.DialogSize or Frame.GetEffectiveMinSize()
    Frame.SetSize((max(x, widget.DIALOG.MIN_SIZE[0]), max(y, UI.SETTINGS["DLG_HEAD"] + widget.DIALOG.MIN_SIZE[1])))
    Frame.SetPosition(widget.DialogPos or UI.EnsureWindowInScreen(widget.Canvas.ClientToScreen(widget.GetPosition() + wx.Point(64, 0)), (x, y)))
    Frame.Main.GetData()
    Frame.Play("FADEIN")
    return Frame.Main


# ======================================================= Dialog =======================================================
class Dialog(UI.BaseMain):
    AUTO = True
    HELP = None
    TASK = False
    SIZE = None
    MIN_SIZE = (120, 40)
    ORIENTATION = wx.VERTICAL
    MARGIN = 2
    LABEL_WIDTH = 80
    LINE_HEIGHT = 24
    BUTTON_WIDTH = 80

    def __init__(self, parent, widget):
        super().__init__(parent, size=self.SIZE or wx.DefaultSize)  # MainFrame - DialogFrame - Dialog
        self.Widget = widget
        self.Frame.SetIcon(widget.__RES__["DIALOG"])
        self.Harbor = self.GetGrandParent().Harbor
        self.Head = None
        self.Sash = None
        self.detached = True
        MainSizer = wx.BoxSizer({"H": wx.HORIZONTAL, "V": wx.VERTICAL}[self.ORIENTATION] if self.ORIENTATION in ("V", "H") else self.ORIENTATION)
        self.AddFieldCtrl(self.Initialize(MainSizer) or MainSizer)
        self.AddStdButton(self.Finalize(MainSizer) or MainSizer)
        self.SetSizer(MainSizer)

    # --------------------------------------
    def AddFieldCtrl(self, sizer):
        self.AutoGet = {}
        self.AutoSet = {}
        if self.AUTO:
            for field in self.Widget.INTERNAL:
                if isinstance(field, str):
                    continue
                key = field.key
                cls = field.__class__
                label = self.L.Get(field.label, "WIDGET_DLG_")
                if "hint" in field.kwargs:
                    field.kwargs["hint"] = self.L.Get(field.kwargs["hint"], "WIDGET_DLG_")
                if issubclass(cls, BooleanField):
                    tags = self.L.Get(field.tags[0], "WIDGET_DLG_"), self.L.Get(field.tags[1], "WIDGET_DLG_")
                    self[key] = self.AddButtonToggle(sizer, label, tags=tags, toggle=self.GetDefaultData(key, 0), **field.kwargs)
                    self.AutoGet[key] = self[key].IsToggled
                    self.AutoSet[key] = self[key].SetToggle
                elif issubclass(cls, (IntegerField, FloatField, LineField)):
                    self[key] = self.AddLineCtrl(sizer, label, value=str(self.GetDefaultData(key, "")), **field.kwargs)
                    self.AutoGet[key] = self[key].GetValue
                    self.AutoSet[key] = self[key].SetValue
                elif issubclass(cls, TextField):
                    self[key] = self.AddTextCtrl(sizer, label, value=self.GetDefaultData(key, ""), **field.kwargs)
                    self.AutoGet[key] = self[key].GetValue
                    self.AutoSet[key] = self[key].SetValue
                elif issubclass(cls, ChoiceField):
                    choices = tuple(self.L.Get(i, "WIDGET_DLG_") if isinstance(i, str) else str(i) for i in field.choices)
                    selected = -1 if self.Widget[key] is None else field.choices.index(self.Widget[key])
                    if field.widget == "L":
                        AddXXX = self.AddListBox
                    elif field.widget == "B":
                        AddXXX = self.AddButtonBundle
                    else:
                        AddXXX = self.AddPickerValue
                    self[key] = AddXXX(sizer, label, choices=choices, selected=selected, **field.kwargs)
                    self.AutoGet[key] = self[key].GetSelection
                    self.AutoSet[key] = self[key].SetSelection
                elif issubclass(cls, FileField):
                    self[key] = self.AddPickerFile(sizer, label, value=self.GetDefaultData(key, ""), **field.kwargs)
                    self.AutoGet[key] = self[key].GetValue
                    self.AutoSet[key] = self[key].SetValue

    def AutoSetData(self):
        ok = True
        for field in self.Widget.INTERNAL:
            if isinstance(field, BaseField):
                v = field.Validate(UI.Do(self.AutoGet[field.key]))
                if v is None:
                    ok = False
                    self.Widget[field.key] = None
                else:
                    self.Widget[field.key] = v
        return ok

    def GetDefaultData(self, key, default):
        if self.Widget[key] is not None:
            return self.Widget[key]
        return default

    # --------------------------------------
    def EnableCanvas(self):
        self.GetGrandParent().Enable()

    def DisableCanvas(self):
        self.GetGrandParent().Disable()

    # --------------------------------------
    def Attach(self):
        if self.detached:
            self.detached = False
            self.Frame.Hide()
            self.Frame.Main = None
            self.Frame.GetSizer().Detach(self)
            self[0].Hide()
            self.Layout()
            if 1 in self:
                self[1].Func = self.OnBegin
            if not self.IsShown():
                self.Show()
            self.Reparent(self.Harbor.Inner)
            self.Head = AttachedHead(self.Harbor.Inner, tag=self.Widget.NAME, pic=self.R["AP_ABORT"][0], func=(self.Harbor.OnChild, self))
            self.Sash = UI.Sash(self.Harbor.Inner, target=self, direction="T", vRange=(2, 600), func=((self.Harbor.SetActualSize,), self.Harbor.Inner.Layout, self.Harbor.ReDraw), res="D")
            self.Harbor.Inner.GetSizer().AddMany((
                (self.Head, SF_HEAD),
                (self, SF_MAIN),
                (self.Sash, SF_SASH)
            ))
            self.Harbor.SetActualSize()
            self.Harbor.ReDraw()
            if not self.Harbor.IsShown():
                self.Harbor.GetParent().HiderR.Click()
            self.Widget.Canvas.ReDraw()

    def Detach(self):
        if not self.detached:
            self.detached = True
            self._RemoveFromHarbor()
            self[0].Show()
            self.Layout()
            if 1 in self:
                self[1].Func = self.OnReady
            if not self.IsShown():
                self.Show()
            self.Reparent(self.Frame)
            self.Frame.Main = self
            self.Frame.GetSizer().Insert(1, self, 1, wx.EXPAND | wx.ALL ^ wx.BOTTOM, 4)
            self.Frame.Layout()
            # self.Frame.Refresh()
            self.Frame.Show()
            self.Frame.SetFocus()
            for i in self.Harbor.Inner.GetChildren():
                if isinstance(i, Dialog):
                    break
            else:
                self.Harbor.GetParent().HiderR.Click()
            self.Widget.Canvas.ReDraw()

    def _RemoveFromHarbor(self):
        self.Harbor.Inner.GetSizer().Detach(self.Head)
        self.Harbor.Inner.GetSizer().Detach(self)
        self.Harbor.Inner.GetSizer().Detach(self.Sash)
        self.Harbor.SetActualSize()
        self.Harbor.ReDraw()
        self.Head.DestroyLater()
        self.Sash.DestroyLater()

    def Locate(self):
        self.Widget.Canvas.Play("LOCATE", [self.Widget for _ in range(10)])

    # --------------------------------------
    def OnClose(self):  # Key = 0
        self.Widget.DialogSize = self.Frame.GetSize()
        self.Widget.DialogPos = self.Frame.GetPosition()
        if self.Frame.minimized:
            self.Widget.DialogSize[1] = self.Frame.minimized
        self.Widget.Dialog = None
        self.Widget.Canvas.ReDraw()
        if self.detached:
            self.Frame.Play("FADEOUT")
        else:
            self._RemoveFromHarbor()
            self.Destroy()
            self.Frame.Destroy()

    def OnReady(self):  # Key = 1
        if self.OnBegin():
            self.OnClose()

    def OnApply(self):  # Key = 2
        if self.AUTO:
            self.AutoSetData()
        self.SetData()
        self.Widget.OnAlter()
        self.Widget.Canvas.ReDraw()

    def OnBegin(self):  # Key = 3
        ok = self.AutoSetData() if self.AUTO else True
        self.SetData()
        self.Widget.OnBegin()
        self.Widget.Canvas.ReDraw()
        return ok

    def OnAbort(self):  # Key = 4
        self.Widget.OnAbort()

    # --------------------------------------
    def AddStdButton(self, sizer):
        size = wx.Size(40, self.LINE_HEIGHT)
        self[0] = UI.ToolNormal(self, size=size, pics=self.R["AP_CROSS"], edge="D", func=self.OnClose)
        if self.Widget.THREAD:
            self[3] = UI.ToolNormal(self, size=size, pics=self.R["AP_BEGIN"], edge="D", func=self.OnBegin)
            self[4] = UI.ToolNormal(self, size=size, pics=self.R["AP_ABORT"], edge="D", func=self.OnAbort)
        elif self.TASK:
            self[3] = UI.ToolNormal(self, size=size, pics=self.R["AP_BEGIN"], edge="D", func=self.OnBegin)
        else:
            self[1] = UI.ToolNormal(self, size=size, pics=self.R["AP_CHECK"], edge="D", func=self.OnReady)
        if self.Widget.INTERNAL or self.Widget.INCOMING:
            self[2] = UI.ToolNormal(self, size=size, pics=self.R["AP_APPLY"], edge="D", func=self.OnApply)
        if sizer.GetOrientation() == wx.HORIZONTAL:
            subSizer = sizer
            sizer.Add(4, 4, 1)
        else:
            subSizer = self.AddPerpendicularSizer(sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 0)
        for i in (3, 4, 1, 0, 2):
            if i in self:
                subSizer.Add(self[i], 0, wx.ALL, self.MARGIN)

    # --------------------------------------
    def Initialize(self, Sizer):
        pass

    def Finalize(self, Sizer):
        pass

    def GetData(self):
        pass

    def SetData(self):
        pass
