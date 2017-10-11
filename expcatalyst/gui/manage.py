# -*- coding: utf-8 -*-


import wx
import DynaUI as UI

# from .dialog import Head

SIZE_BUTTON = wx.Size(100, 36)
SIZE_18BY18 = wx.Size(18, 18)
SIZE_36BY36 = wx.Size(36, 36)

SizerFlagsHead = wx.SizerFlags().Border(wx.ALL, 3)
SizerFlagsMain = wx.SizerFlags().Border(wx.ALL, 4)
SizerFlagsItem = wx.SizerFlags().Center()

SizerFlagsTitle = wx.SizerFlags().Expand().Border(wx.ALL ^ wx.BOTTOM, 4)
SizerFlagsPanel = wx.SizerFlags().Expand().Border(wx.ALL ^ wx.TOP, 4)
SizerFlagsNew = wx.SizerFlags().Expand().Border(wx.ALL, 4)


# ======================================================== Main ========================================================
class Main(UI.Scrolled):
    def __init__(self, parent):
        super().__init__(parent, edge=None)
        # MainFrame -> BaseDialog -> Main
        self.MainFrame = self.GetGrandParent()
        self.AddScrollBar((0, 12))
        SizerLeft = wx.BoxSizer(wx.VERTICAL)
        SizerLeft.AddMany((
            (UI.ToolNormal(self, size=SIZE_BUTTON, pics=(self.R["AP_ARROW_D"], "L", 4), tag=(self.L["MANAGE_LOAD"], "L", 28), edge="EM", func=self.OnLoad, showTag=True), SizerFlagsMain),
            (UI.ToolNormal(self, size=SIZE_BUTTON, pics=(self.R["AP_ARROW_U"], "L", 4), tag=(self.L["MANAGE_SAVE"], "L", 28), edge="EM", func=self.OnSave, showTag=True), SizerFlagsMain),
            (UI.ToolNormal(self, size=SIZE_BUTTON, pics=(self.R["AP_RESET"], "L", 4), tag=(self.L["MANAGE_RESET"], "L", 28), edge="EM", func=self.OnReset, showTag=True), SizerFlagsMain),
            (UI.ToolNormal(self, size=SIZE_BUTTON, pics=(self.R["AP_CHECK"], "L", 4), tag=(self.L["DIALOG_READY"], "L", 28), edge="EM", func=self.OnReady, showTag=True), SizerFlagsMain),
            (UI.ToolNormal(self, size=SIZE_BUTTON, pics=(self.R["AP_CROSS"], "L", 4), tag=(self.L["DIALOG_CLOSE"], "L", 28), edge="EM", func=self.OnClose, showTag=True), SizerFlagsMain),
            (UI.ToolNormal(self, size=SIZE_BUTTON, pics=(self.R["AP_APPLY"], "L", 4), tag=(self.L["DIALOG_APPLY"], "L", 28), edge="EM", func=self.OnApply, showTag=True), SizerFlagsMain)
        ))
        SizerRight = wx.BoxSizer(wx.VERTICAL)
        self.Outer = wx.Panel(self)
        self.Inner = wx.Panel(self.Outer, pos=(0, 0))
        self.Inner.R = self.R
        self.Inner.S = self.S
        self.Inner.L = self.L
        InnerSizer = wx.BoxSizer(wx.VERTICAL)
        self.Inner.SetSizer(InnerSizer)
        SizerRight.Add(self.Outer, 1, wx.EXPAND)
        Sizer = wx.BoxSizer(wx.HORIZONTAL)
        Sizer.Add(SizerLeft, 0, wx.EXPAND | wx.ALL ^ wx.RIGHT, 4)
        Sizer.Add(SizerRight, 1, wx.EXPAND | wx.ALL, 4)
        Sizer.Add(UI.SETTINGS["SCROLL_DIAMETER"], 4)
        self.SetSizer(Sizer)

        self.newGroupIndex = 1
        self["NEW"] = None
        self.Groups = {}
        self.AddItems(self.MainFrame.WidgetList)

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
    def OnLoad(self):
        pass  # TODO

    def OnSave(self):
        pass  # TODO

    def OnReset(self):
        self.ClearItems()
        self.AddItems(self.MainFrame.WidgetList)

    def OnReady(self):
        self.OnApply()
        self.OnClose()

    def OnClose(self):
        self.GetParent().Play("FADEOUT")

    def OnApply(self):
        widgetList = []
        for sizerItem in self.Inner.GetSizer().GetChildren():
            window = sizerItem.GetWindow()
            if isinstance(window, GroupTitle):
                if window.group != self.L["GROUP_NONE"]:
                    widgetList.append(window.group)
                    for item in self.Groups[window.group]["PANEL"].GetSizer().GetChildren():
                        if isinstance(item.GetWindow(), WidgetItem):
                            widgetList.append(item.GetWindow().Item)
        if len(self.Groups[self.L["GROUP_NONE"]]["PANEL"].GetChildren()) > 2:
            widgetList.append(self.L["GROUP_NONE"])
            for sizerItem in self.Groups[self.L["GROUP_NONE"]]["PANEL"].GetSizer().GetChildren():
                window = sizerItem.GetWindow()
                if isinstance(window, WidgetItem):
                    widgetList.append(window.Item)
        self.MainFrame.WidgetList = widgetList
        self.MainFrame.WidgetDict = {i[1].__name__: i[1] for i in widgetList if not isinstance(i, str)}
        self.MainFrame.Gadget.ClearItems()
        self.MainFrame.Gadget.AddItems(widgetList)

    # --------------------------------------
    def AddItems(self, args):
        self.Freeze()
        group = self.NewGroup(self.L["GROUP_NONE"])
        for arg in args:
            if isinstance(arg, (tuple, list)):
                self.AddItem(WidgetItem(self.Groups[group]["PANEL"], item=arg, group=group))
            else:
                group = self.NewGroup(arg or self.L["GROUP_NONE"])
        self["NEW"] = UI.Button(self.Inner, size=wx.Size(-1, 64), tag=self.L["MANAGE_NEW_GROUP"], func=(self.NewGroup, None, True), res="L", edge="D")
        self.Inner.GetSizer().Add(self["NEW"], SizerFlagsNew)
        self.Inner.Layout()
        self.OnSize()
        self.Thaw()

    def ClearItems(self):
        self.Freeze()
        self.Inner.DestroyChildren()
        self.newGroupIndex = 1
        self["NEW"] = None
        self.Groups = {}
        self.Thaw()

    def NewGroup(self, group=None, layout=False):
        if group is None:
            while "%s %s" % (self.L["GROUP_NEW"], self.newGroupIndex) in self.Groups:
                self.newGroupIndex += 1
            group = "%s %s" % (self.L["GROUP_NEW"], self.newGroupIndex)
        else:
            if group in self.Groups:
                return group
        panel = UI.BaseControl(self.Inner)
        title = GroupTitle(self.Inner, group)
        groupSizer = wx.WrapSizer()
        btnAdd = UI.Button(panel, size=SIZE_36BY36, pic=self.R["MANAGE_ADD"], func=None, edge=None, res="L")
        groupSizer.Add(btnAdd, SizerFlagsItem)
        btnDel = UI.Button(panel, size=SIZE_36BY36, pic=self.R["MANAGE_DEL"], func=(self.DelGroup, title), edge=None, res="L")
        groupSizer.Add(btnDel, SizerFlagsItem)
        panel.SetSizer(groupSizer)
        self.Inner.GetSizer().AddMany(((title, SizerFlagsTitle), (panel, SizerFlagsPanel)))
        self.Groups[group] = {"TITLE": title, "PANEL": panel, "ADD": btnAdd, "DEL": btnDel}
        if self["NEW"]:
            self.Inner.GetSizer().Detach(self["NEW"])
            self.Inner.GetSizer().Add(self["NEW"], SizerFlagsNew)
        if layout:
            self.OnArrangement()
        return group

    def DelGroup(self, title):
        group = title.group
        if group == self.L["GROUP_NONE"]:
            return
        for child in self.Groups[group]["PANEL"].GetChildren():
            if isinstance(child, WidgetItem):
                child.ChangeGroup(self.L["GROUP_NONE"], None, False)
        sizer = self.Inner.GetSizer()
        sizer.Detach(self.Groups[group]["TITLE"])
        sizer.Detach(self.Groups[group]["PANEL"])
        self.Groups[group]["TITLE"].Destroy()
        self.Groups[group]["PANEL"].Destroy()
        del self.Groups[group]
        self.OnArrangement()

    def AddItem(self, item, index=None, layout=False):
        sizer = item.GetParent().GetSizer()
        index = sizer.GetItemCount() - 2 if index is None else min(index, sizer.GetItemCount() - 2)
        sizer.Insert(index, item, SizerFlagsItem)
        item.currentIndex = index
        if layout:
            self.OnArrangement()

    def DelItem(self, item, layout=False):
        item.GetParent().GetSizer().Detach(item)
        item.Destroy()
        if layout:
            self.OnArrangement()

    def OnArrangement(self):
        self.Inner.Layout()
        self.OnSize()
        self.ReDraw()


# ======================================================= Title ========================================================
class GroupTitle(UI.Button):  # TODO
    def __init__(self, parent, group):
        self.group = group
        isNoGroup = group == parent.L["GROUP_NONE"]
        super().__init__(parent, size=wx.Size(-1, 20), tag=group, func=None if isNoGroup else self.ShowNameChange, edge="D")
        # MiniFrame - Main - Outer - Inner - Title
        self.Main = parent.GetGrandParent()
        if not isNoGroup:
            self.Text = UI.Text(self, style=wx.TE_CENTER | wx.SIMPLE_BORDER)
            self.Text.SetMaxLength(20)
            self.Text.Hide()
            self.Text.Bind(wx.EVT_KILL_FOCUS, self.OnTextLost)
            self.Text.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnter)
            Sizer = wx.BoxSizer(wx.HORIZONTAL)
            Sizer.Add(UI.ToolNormal(self, size=wx.Size(20, 20), pics=self.R["AP_TRIANGLE_U"], func=(self.OnMove, "U"), edge=("", "LTB")))
            Sizer.Add(self.Text, 1, wx.EXPAND)
            Sizer.Add(0, 0, 1)
            Sizer.Add(UI.ToolNormal(self, size=wx.Size(20, 20), pics=self.R["AP_TRIANGLE_D"], func=(self.OnMove, "D"), edge=("", "RTB")))
            self.SetSizer(Sizer)

    def ShowNameChange(self):
        self.GetSizer().GetChildren()[2].SetProportion(0)
        self.Text.SetValue(self.group)
        self.Text.Show()
        self.Text.SetFocus()
        self.Layout()

    def HideNameChange(self):
        self.GetSizer().GetChildren()[2].SetProportion(1)
        self.Text.Hide()
        self.Layout()

    def OnTextLost(self, evt):
        self.HideNameChange()
        evt.Skip()

    def OnTextEnter(self, evt):
        new = self.Text.GetValue()
        if new == self.group:
            self.HideNameChange()
        elif new in self.Main.Groups:
            wx.Bell()
        elif new:
            self.OnChangeName(new)
            self.HideNameChange()

    def OnChangeName(self, new):
        self.Main.Groups[new] = self.Main.Groups[self.group]
        del self.Main.Groups[self.group]
        for item in self.Main.Groups[new]["PANEL"].GetChildren():
            if isinstance(item, WidgetItem):
                item.group = new
        self.group = new
        self.SetTag(new)
        self.Positioning()
        self.ReDraw()

    def OnMove(self, d):
        Sizer = self.GetParent().GetSizer()
        index = Sizer.GetChildren().index(Sizer.GetItem(self))
        panel = Sizer.GetItem(index + 1).GetWindow()
        if d == "U":
            index = max(index - 2, 2)
        elif d == "D":
            index = min(index + 2, Sizer.GetItemCount() - 3)
        Sizer.Detach(self)
        Sizer.Detach(panel)
        Sizer.Insert(index, self, SizerFlagsTitle)
        Sizer.Insert(index + 1, panel, SizerFlagsPanel)
        self.Main.OnArrangement()


# ======================================================== Item ========================================================
class WidgetItem(UI.Button):
    def __init__(self, parent, item, group):
        super().__init__(parent, size=wx.Size(108, 36), tag=("\n".join(item[1].NAME.split()), "L", 38), pic=(parent.R["WIDGET_BUTTON"][item[1].KEY], "L", 2), res="L", edge=None)
        self.Item = item
        # Main - Outer - Inner - Title/Panel - Item
        self.Inner = self.GetGrandParent()
        self.Main = self.Inner.GetGrandParent()
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.group = group
        self.todo = None
        self.index = None
        self.pointing = None
        self.leftDown = False
        self.currentIndex = None

    def ChangeGroup(self, group=None, index=None, layout=True):
        self.group = group if group else self.Main.NewGroup()
        self.GetParent().GetSizer().Detach(self)
        self.Reparent(self.Main.Groups[self.group]["PANEL"])
        self.Main.AddItem(self, index, layout)

    def OnMouse(self, evt):
        evtType = evt.GetEventType()
        if evtType == wx.wxEVT_LEFT_DOWN:
            if not self.HasCapture(): self.CaptureMouse()
            self.leftDown = True
            self.SetCursor(self.R["WIDGET_CURSOR"][self.Item[1].KEY])
        elif evtType == wx.wxEVT_LEFT_UP:
            if self.HasCapture(): self.ReleaseMouse()
            UI.Do(self.todo)
            if self.pointing:
                self.pointing.Play("LEAVE")
            self.todo = None
            self.pointing = None
            self.leftDown = False
            self.SetCursor(self.R["CURSOR_NORMAL"])
        elif evtType == wx.wxEVT_MOTION and self.leftDown:
            pos = self.ClientToScreen(evt.GetPosition())
            if self.Main.Groups[self.group]["PANEL"].GetScreenRect().Contains(pos):
                if self.Main.Groups[self.group]["DEL"].GetScreenRect().Contains(pos):
                    self.todo = (wx.CallAfter, self.Main.DelItem, self, True)
                    pointing = self.Main.Groups[self.group]["DEL"]
                else:
                    W, H = self.Main.Groups[self.group]["PANEL"].GetSize()
                    C, R = W // 108, H // 36
                    x, y = self.Main.Groups[self.group]["PANEL"].ScreenToClient(pos)
                    c, r = max(min(x // 108, C), 0), max(min(y // 36, R), 0)
                    index = r * C + c
                    if index != self.currentIndex:
                        self.GetParent().GetSizer().Detach(self)
                        self.Main.AddItem(self, max(0, index), True)
                    self.todo = None
                    pointing = self.Main.Groups[self.group]["TITLE"]
            elif self.Main.Groups[self.group]["TITLE"].GetScreenRect().Contains(pos):
                self.todo = None
                pointing = self.Main.Groups[self.group]["TITLE"]
            else:
                for group in self.Main.Groups:
                    if group != self.group:
                        if self.Main.Groups[group]["TITLE"].GetScreenRect().Contains(pos):
                            self.todo = None
                            pointing = self.Main.Groups[group]["TITLE"]
                            self.ChangeGroup(group)
                            break
                        if self.Main.Groups[group]["PANEL"].GetScreenRect().Contains(pos):
                            self.todo = None
                            pointing = self.Main.Groups[group]["TITLE"]
                            self.ChangeGroup(group)
                            break
                else:
                    if self.Main["NEW"].GetScreenRect().Contains(pos):
                        self.todo = self.ChangeGroup
                        pointing = self.Main["NEW"]
                    else:
                        self.todo = None
                        pointing = None
            if pointing != self.pointing:
                if pointing:
                    pointing.Play("ENTER")
                if self.pointing:
                    self.pointing.Play("LEAVE")
                self.pointing = pointing
        evt.Skip()

    def OnCaptureLost(self, evt):
        if self.pointing:
            self.pointing.Play("LEAVE")
        self.todo = None
        self.pointing = None
        self.leftDown = False
        self.SetCursor(self.R["CURSOR_NORMAL"])


# ======================================================= Manage =======================================================
class Manage(UI.BaseDialog):
    def __init__(self, parent):
        super().__init__(parent=parent, title=parent.L["MANAGE_TITLE"], size=wx.Size(500, 480), style=wx.STAY_ON_TOP, main=Main)
        self.Head.GetSizer().Insert(0, UI.ToolNormal(self.Head, size=SIZE_18BY18, pics=self.R["AP_HELP"], edge=None, func=(parent.OnDialog, "MANAGE_HELP", "SIMPLE_TEXT", self.L["MANAGE_HELP_HEAD"], self.L["MANAGE_HELP_TEXT"])),
                                    SizerFlagsHead)
        self.Head.SetTagOffset(24, 0)
        self.Center()
        self.Layout()
        self.Play("FADEIN")
