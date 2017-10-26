# -*- coding: utf-8 -*-


import wx
import DynaUI as UI

SizerFlagsTitle = wx.SizerFlags().Expand().Border(wx.TOP, 2)
SizerFlagsPanel = wx.SizerFlags().Expand().Border(wx.BOTTOM, 6)


# ======================================================= Gadget =======================================================
class Gadget(UI.Scrolled):
    def __init__(self, parent, size):
        super().__init__(parent, size=size, edge="H")
        self.AddScrollBar((0, 12))
        self.Tool = UI.Tool(self, size=wx.Size(-1, 26), itemSize=wx.Size(24, 24), bg="D", edge="EM")
        self.Tool.SizerFlags1 = wx.SizerFlags().Expand().Border(wx.TOP | wx.BOTTOM, 1)
        self.Tool.SizerFlags2 = wx.SizerFlags().Center().Border(wx.TOP | wx.BOTTOM, 1)
        self.Tool.AddItems(1,
                           ("T", "TOOL_T_SHOW", self.OnGroup, {"toggle": True}),
                           ("T", "TOOL_T_TEXT", self.OnLabel, {"toggle": True}), "|", "|",
                           ("N", "TOOL_MANAGE", (parent.OnDialog, "M", "MANAGE")),
                           1)
        self.Tool["GADGET_SEARCH"] = UI.Text(self.Tool, size=wx.Size(-1, 20), style=wx.BORDER_NONE)
        self.Tool["GADGET_SEARCH"].Bind(wx.EVT_TEXT, self.OnSearch)
        self.Tool["GADGET_SEARCH"].Bind(wx.EVT_ENTER_WINDOW, lambda evt: self.GetParent().SetStatus(self.L["GADGET_SEARCH"]))
        self.Tool["GADGET_CANCEL"] = UI.Button(self.Tool, size=wx.Size(24, 24), tag="x", edge=None, func=self.OnCancel)
        self.Tool["GADGET_CANCEL"].SetTip(self.GetParent().SetStatus, self.L["GADGET_CANCEL"])
        self.Tool.GetSizer().Insert(4, self.Tool["GADGET_CANCEL"], self.Tool.SizerFlags2)
        self.Tool.GetSizer().Insert(4, self.Tool["GADGET_SEARCH"], 1, wx.ALIGN_BOTTOM | wx.TOP | wx.BOTTOM, 1)
        self.Outer = wx.Panel(self)
        self.Inner = wx.Panel(self.Outer, pos=(0, 0))
        self.Inner.R = self.R
        self.Inner.S = self.S
        self.Inner.L = self.L
        self.Inner.SetSizer(wx.BoxSizer(wx.VERTICAL))
        MainSizer = wx.BoxSizer(wx.VERTICAL)
        MainSizer.Add(self.Tool, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        MainSizer.Add(self.Outer, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        Sizer = wx.BoxSizer(wx.HORIZONTAL)
        Sizer.Add(MainSizer, 1, wx.EXPAND | wx.ALL, 4)
        Sizer.Add(UI.SETTINGS["SCROLL_DIAMETER"], 4)
        self.SetSizer(Sizer)

        self.Groups = {}
        self.showGroup = True
        self.showLabel = True

    # --------------------------------------
    def SetActualSize(self):
        super().SetActualSize()
        self.Inner.SetSize(self.ASize)

    def SetOffset(self, *args):
        super().SetOffset(*args)
        self.Inner.SetPosition((0, -self.GetViewPoint()[1]))

    def CalculateActualSize(self):
        return self.Outer.GetSize()[0], self.Inner.GetEffectiveMinSize()[1] + 36

    def OnSize(self):
        self.Inner.SetSize(wx.Size(self.Outer.GetSize()[0], self.Inner.GetEffectiveMinSize()[1] + 36))
        self.SetActualSize()

    # --------------------------------------
    def AddItems(self, args):
        setStatus = self.GetParent().SetStatus
        sizer = self.Inner.GetSizer()
        group = self.L["GROUP_NONE"]
        groupSizer = None
        self.Freeze()
        for arg in args:
            if isinstance(arg, (tuple, list)):
                item = GadgetItem(self.Groups[group]["PANEL"], item=arg[1])
                item.SetTip(setStatus, arg[1].NAME)
                groupSizer.Add(item)
                self.Groups[group]["ITEMS"].append(item)
            else:
                group = self.L.Get(arg, "WIDGET_GROUP_") or self.L["GROUP_NONE"]
                if group in self.Groups:
                    groupSizer = self.Groups[group]["PANEL"].GetSizer()
                else:
                    groupSizer = wx.WrapSizer()
                    title = UI.Button(self.Inner, size=(-1, 20), tag=(" ■ " + group, "L"), func=(self.OnGroup, group))
                    title.SetTip(setStatus, group)
                    panel = UI.BaseControl(self.Inner)
                    panel.SetSizer(groupSizer)
                    sizer.AddMany(((title, SizerFlagsTitle), (panel, SizerFlagsPanel)))
                    self.Groups[group] = {"TITLE": title, "PANEL": panel, "SHOW": True, "ITEMS": []}
        self.Inner.Layout()
        self.OnSize()
        self.Thaw()

    def ClearItems(self):
        self.Inner.DestroyChildren()
        self.Groups = {}
        self.Tool["GADGET_SEARCH"].ChangeValue("")
        if not self.showGroup:
            self.Tool["GADGET_GROUP"].Click()
        if not self.showLabel:
            self.Tool["GADGET_LABEL"].Click()

    # --------------------------------------
    def OnSearch(self, evt):
        text = self.Tool["GADGET_SEARCH"].GetValue().lower()
        self.Freeze()
        if text:
            for group in self.Groups:
                show = showGroup = text in group.lower()
                for item in self.Groups[group]["ITEMS"]:
                    showItem = text in item.Item.NAME.lower()
                    show |= showItem
                    item.Show(showItem or showGroup)
                self.DoToggleGroup(group, show)
        else:
            for group in self.Groups:
                for item in self.Groups[group]["ITEMS"]:
                    item.Show(True)
                self.DoToggleGroup(group, self.showGroup)
        self.Inner.Layout()
        self.SetActualSize()
        self.Thaw()

    def OnCancel(self):
        self.Tool["GADGET_SEARCH"].Clear()

    def OnGroup(self, group=None):
        self.Freeze()
        if group is None:
            self.showGroup = not self.showGroup
            for group in self.Groups:
                self.DoToggleGroup(group, self.showGroup)
        else:
            self.DoToggleGroup(group, not self.Groups[group]["SHOW"])
        self.Inner.Layout()
        self.SetActualSize()
        self.Thaw()

    def DoToggleGroup(self, group, show):
        self.Groups[group]["SHOW"] = show
        self.Groups[group]["PANEL"].Show(show)
        self.Groups[group]["TITLE"].SetTag((" □ ", " ■ ")[show] + group)

    def OnLabel(self):
        self.showLabel = not self.showLabel
        size = (108 if self.showLabel else 36, 36)
        self.Freeze()
        for group in self.Groups:
            for item in self.Groups[group]["ITEMS"]:
                item.SetInitialSize(size)
        self.Inner.Layout()
        self.SetActualSize()
        self.Thaw()


# ===================================================== GadgetItem =====================================================
class GadgetItem(UI.Button):
    def __init__(self, parent, item):
        super().__init__(parent, size=wx.Size(108, 36), tag=("\n".join(item.NAME.split()), "L", 38), pic=(parent.R["WIDGET_BUTTON"][item.KEY], "L", 2), res="L", edge=None)
        self.Item = item
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Canvas = self.GetTopLevelParent().Canvas
        self.leftDown = False

    def OnMouse(self, evt):
        evtType = evt.GetEventType()
        if evtType == wx.wxEVT_LEFT_DOWN:
            if not self.HasCapture(): self.CaptureMouse()
            self.leftDown = True
        elif evtType == wx.wxEVT_LEFT_UP:
            if self.HasCapture(): self.ReleaseMouse()
            screenPos = self.ClientToScreen(evt.GetPosition())
            if self.Canvas.GetScreenRect().Contains(screenPos):
                self.Canvas.AddWidget(self.Item, self.Canvas.ScreenToClient(screenPos) - (13, 13))
            self.leftDown = False
            self.SetCursor(self.R["CURSOR_NORMAL"])
        elif evtType == wx.wxEVT_LEFT_DCLICK:
            self.Canvas.AddWidget(self.Item)
        elif evtType == wx.wxEVT_MOTION and self.leftDown:
            self.leftDown = False
            self.SetCursor(self.R["WIDGET_CURSOR"][self.Item.KEY])
        evt.Skip()

    def OnCaptureLost(self, evt):
        self.leftDown = False
        self.SetCursor(self.R["CURSOR_NORMAL"])
