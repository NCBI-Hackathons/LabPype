# -*- coding: utf-8 -*-

import wx
import DynaUI as UI

SF_TITLE = wx.SizerFlags().Expand().Border(wx.TOP, 2)
SF_PANEL = wx.SizerFlags().Expand().Border(wx.BOTTOM, 6)


# ======================================================= Gadget =======================================================
class Gadget(UI.Scrolled):
    def __init__(self, parent, size):
        super().__init__(parent, size=size, edge="H")
        self.F = parent
        self.AddScrollBar((0, 12))
        self.Tool = UI.Tool(self, size=wx.Size(-1, 26), itemSize=wx.Size(24, 24), bg="D", edge="EM")
        self.Tool.SizerFlags1 = wx.SizerFlags().Expand().Border(wx.TOP | wx.BOTTOM, 1)
        self.Tool.SizerFlags2 = wx.SizerFlags().Center().Border(wx.TOP | wx.BOTTOM, 1)
        self.Tool.AddItems(1,
                           ("T", "TOOL_T_SHOW", self.OnGroup, {"toggle": self.S["TOGGLE_G_GROUP"]}),
                           ("T", "TOOL_T_TEXT", self.OnLabel, {"toggle": self.S["TOGGLE_G_LABEL"]}), "|", "|",
                           ("N", "TOOL_MANAGE", parent.OnShowManage),
                           1)
        self.Tool["GADGET_SEARCH"] = UI.Text(self.Tool, size=wx.Size(-1, 20), style=wx.BORDER_NONE)
        self.Tool["GADGET_SEARCH"].Bind(wx.EVT_TEXT, self.OnSearch)
        self.Tool["GADGET_SEARCH"].Bind(wx.EVT_ENTER_WINDOW, lambda evt: self.F.SetStatus(self.L["GADGET_SEARCH"]))
        self.Tool["GADGET_CANCEL"] = UI.Button(self.Tool, size=wx.Size(24, 24), tag="x", edge=None, func=self.OnCancel)
        self.Tool["GADGET_CANCEL"].SetTip(self.F.SetStatus, self.L["GADGET_CANCEL"])
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

        self.Groups = {}  # {"TITLE": title, "PANEL": panel, "SHOW": True, "ITEMS": [gadgetItem, ...]}

    # --------------------------------------
    def SetActualSize(self):
        super().SetActualSize()
        self.Inner.SetSize(self.ASize)

    def SetOffset(self, *args):
        super().SetOffset(*args)
        self.Inner.SetPosition((0, -self.GetViewPoint()[1]))

    def CalculateActualSize(self):
        return self.Outer.GetSize()[0], self.Inner.GetEffectiveMinSize()[1] + 48

    def OnSize(self):
        self.Inner.SetSize(wx.Size(self.Outer.GetSize()[0], self.Inner.GetEffectiveMinSize()[1] + 48))
        self.SetActualSize()

    # --------------------------------------
    def AddItems(self, args):
        itemSize = wx.Size(120, 48) if self.S["TOGGLE_G_LABEL"] else wx.Size(40, 48)
        pic = self.R["AP_ABORT" if self.S["TOGGLE_G_GROUP"] else "AP_MINI"][0]
        sizer = self.Inner.GetSizer()
        group = self.L["GROUP_NONE"]
        groupSizer = None
        self.Freeze()
        for arg in args:
            if isinstance(arg, str):
                group = arg or self.L["GROUP_NONE"]
                if group in self.Groups:
                    groupSizer = self.Groups[group]["PANEL"].GetSizer()
                else:
                    groupSizer = wx.WrapSizer()
                    title = UI.Button(self.Inner, size=wx.Size(-1, 20), tag=(group, "L", 20), pic=(pic, "L"), func=(self.OnGroup, group), fg="B")
                    title.SetTip(self.F.SetStatus, group)
                    panel = UI.BaseControl(self.Inner)
                    panel.SetSizer(groupSizer)
                    panel.Show(self.S["TOGGLE_G_GROUP"])
                    sizer.AddMany(((title, SF_TITLE), (panel, SF_PANEL)))
                    self.Groups[group] = {"TITLE": title, "PANEL": panel, "SHOW": self.S["TOGGLE_G_GROUP"], "ITEMS": []}
            else:
                item = GadgetItem(self.Groups[group]["PANEL"], item=arg, size=itemSize)
                item.SetTip(self.F.SetStatus, arg.NAME)
                groupSizer.Add(item)
                self.Groups[group]["ITEMS"].append(item)
        self.Inner.Layout()
        self.OnSize()
        self.Thaw()

    def DelItems(self, args):
        self.Freeze()
        for arg in args:
            if not isinstance(arg, str):
                if arg in self.F.M.Groups:
                    group = self.L["GROUP_NONE"]
                    for i in range(self.F.M.Groups.index(arg), -1, -1):
                        if isinstance(self.F.M.Groups[i], str):
                            group = self.F.M.Groups[i]
                            break
                    item = [i for i in self.Groups[group]["ITEMS"] if i.Item is arg][0]
                    item.Destroy()
                    self.Groups[group]["ITEMS"].remove(item)
        for arg in args:
            if isinstance(arg, str):
                if arg in self.Groups:
                    if not self.Groups[arg]["ITEMS"]:
                        self.Groups[arg]["TITLE"].Destroy()
                        self.Groups[arg]["PANEL"].Destroy()
                        del self.Groups[arg]
        self.Inner.Layout()
        self.OnSize()
        self.Thaw()

    def ClearItems(self):
        self.Inner.DestroyChildren()
        self.Groups = {}
        self.Tool["GADGET_SEARCH"].ChangeValue("")

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
                self.DoToggleGroup(group, self.S["TOGGLE_G_GROUP"])
        self.Inner.Layout()
        self.SetActualSize()
        self.Thaw()

    def OnCancel(self):
        self.Tool["GADGET_SEARCH"].Clear()

    def OnGroup(self, group=None):
        self.Freeze()
        if group is None:
            self.S["TOGGLE_G_GROUP"] = not self.S["TOGGLE_G_GROUP"]
            for group in self.Groups:
                self.DoToggleGroup(group, self.S["TOGGLE_G_GROUP"])
        else:
            self.DoToggleGroup(group, not self.Groups[group]["SHOW"])
        self.Inner.Layout()
        self.SetActualSize()
        self.Thaw()

    def DoToggleGroup(self, group, show):
        self.Groups[group]["SHOW"] = show
        self.Groups[group]["PANEL"].Show(show)
        self.Groups[group]["TITLE"].SetPic(self.R["AP_ABORT" if show else "AP_MINI"][0])

    def OnLabel(self):
        self.S["TOGGLE_G_LABEL"] = not self.S["TOGGLE_G_LABEL"]
        size = (120 if self.S["TOGGLE_G_LABEL"] else 40, 48)
        self.Freeze()
        for group in self.Groups:
            for item in self.Groups[group]["ITEMS"]:
                item.SetInitialSize(size)
        self.Inner.Layout()
        self.SetActualSize()
        self.Thaw()


# ===================================================== GadgetItem =====================================================
class GadgetItem(UI.Button):
    def __init__(self, parent, item, size):
        super().__init__(parent, size=size, tag=("\n".join(item.NAME.split()), "L", 40), pic=(item.__RES__["BUTTON"], "L", 4), res="L", edge=None)
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
            self.SetCursor(self.Item.__RES__["CURSOR"])
        evt.Skip()

    def OnCaptureLost(self, evt):
        self.leftDown = False
        self.SetCursor(self.R["CURSOR_NORMAL"])
