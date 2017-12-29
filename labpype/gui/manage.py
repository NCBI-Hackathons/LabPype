# -*- coding: utf-8 -*-

import os
import wx
import threading
import urllib.request
import urllib.parse
import DynaUI as UI
from ..utility import Thread, Interrupted

SIZE_S = wx.Size(80, 24)
SIZE_B = wx.Size(200, 24)
SF_S = wx.SizerFlags().Border(wx.ALL, 4).Expand()
SF_B = wx.SizerFlags().Border(wx.ALL, 2).Proportion(1)

SF_ITEM = wx.SizerFlags().Center()
SF_TITLE = wx.SizerFlags().Expand().Border(wx.ALL ^ wx.BOTTOM, 4)
SF_PANEL = wx.SizerFlags().Expand().Border(wx.ALL ^ wx.TOP, 4)
SF_NEW = wx.SizerFlags().Expand().Border(wx.ALL, 4)


# ======================================================== Main ========================================================
class Main(UI.Scrolled):
    def __init__(self, parent):
        super().__init__(parent, edge=None)
        self.F = parent.GetParent()  # MainFrame -> BaseDialog -> Main
        self.AddScrollBar((0, 12))

        SizerLeft = wx.BoxSizer(wx.VERTICAL)
        self.Installed = UI.ListCtrl(self, data=(), width=(-1,))
        SizerLeft.AddMany((
            (self.Installed, 1, wx.EXPAND | wx.ALL, 4),
            (UI.ToolNormal(self, size=SIZE_B, pics=(self.R["AP_CLOUD"], "L", 8), tag=(self.L["MANAGE_PKG_REMOTE"], "L", 32), edge="D", func=self.OnRemote, showTag=True), SF_S),
            (UI.ToolNormal(self, size=SIZE_B, pics=(self.R["AP_LOCAL"], "L", 8), tag=(self.L["MANAGE_PKG_BROWSE"], "L", 32), edge="D", func=self.OnBrowse, showTag=True), SF_S),
            (UI.ToolNormal(self, size=SIZE_B, pics=(self.R["AP_TRASH"], "L", 8), tag=(self.L["MANAGE_PKG_REMOVE"], "L", 32), edge="D", func=self.OnRemove, showTag=True), SF_S),
        ))

        SizerButton = wx.BoxSizer(wx.HORIZONTAL)
        SizerButton.AddMany((
            (UI.ToolNormal(self, size=SIZE_S, pics=(self.R["AP_RESET"], "L", 8), tag=(self.L["GENERAL_RESET"], "L", 32), edge="D", func=self.OnReset, showTag=True), SF_B),
            (UI.ToolNormal(self, size=SIZE_S, pics=(self.R["AP_CROSS"], "L", 8), tag=(self.L["GENERAL_CLOSE"], "L", 32), edge="D", func=self.OnClose, showTag=True), SF_B),
            (UI.ToolNormal(self, size=SIZE_S, pics=(self.R["AP_CHECK"], "L", 8), tag=(self.L["GENERAL_READY"], "L", 32), edge="D", func=self.OnReady, showTag=True), SF_B),
            (UI.ToolNormal(self, size=SIZE_S, pics=(self.R["AP_APPLY"], "L", 8), tag=(self.L["GENERAL_APPLY"], "L", 32), edge="D", func=self.OnApply, showTag=True), SF_B)
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
        SizerRight.Add(SizerButton, 0, wx.EXPAND | wx.ALL, 2)
        Sizer = wx.BoxSizer(wx.HORIZONTAL)
        Sizer.Add(SizerLeft, 0, wx.EXPAND | wx.ALL, 4)
        Sizer.Add(UI.Separator(self), 0, wx.EXPAND | wx.ALL, 8)
        Sizer.Add(SizerRight, 1, wx.EXPAND | wx.ALL, 4)
        Sizer.Add(UI.SETTINGS["SCROLL_DIAMETER"], 4)
        self.SetSizer(Sizer)

        self.newGroupIndex = 1
        self["NEW"] = None
        self.Groups = {}
        self.UpdatePackageList()
        self.AddItems(self.F.M.Groups)

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
    def UpdatePackageList(self):
        self.Installed.SetData([(i,) for i in self.F.M.GetPackages()])
        self.Installed.ReDraw()

    def OnRemote(self):
        self.F.OnMakeDialog("MANAGE_HEAD_REMOTE", Downloader)

    def OnBrowse(self):
        fp = UI.ShowOpenFileDialog(self, self.L["MSG_PKG_INSTALL_HEAD"], "Zip files (*.zip)|*.zip")
        if fp is not None:
            self.DoInstall(fp)

    def DoInstall(self, fp):
        self.F.M.Install(fp)
        self.UpdatePackageList()

    def OnRemove(self):
        if self.Installed.HasSelection():
            self.F.M.DelPackage(self.Installed.GetStringSelection())
            self.UpdatePackageList()

    def OnReset(self):
        self.ClearItems()
        self.AddItems(sum((self.F.M.Packages[pkgName].__RAW_GROUP__ for pkgName in self.F.M.Packages), []))

    def OnReady(self):
        self.OnApply()
        self.OnClose()

    def OnClose(self):
        if self.F.D.get("PACKAGE_DOWNLOAD"):
            self.F.D["PACKAGE_DOWNLOAD"].SetFocus()
        elif self.F.D.get("PACKAGE_INSTALL"):
            self.F.D["PACKAGE_INSTALL"].SetFocus()
        else:
            self.GetParent().Play("FADEOUT")

    def OnApply(self):
        group = []
        for sizerItem in self.Inner.GetSizer().GetChildren():
            window = sizerItem.GetWindow()
            if isinstance(window, GroupTitle):
                if window.group != self.L["GROUP_NONE"]:
                    group.append(window.group)
                    for item in self.Groups[window.group]["PANEL"].GetSizer().GetChildren():
                        if isinstance(item.GetWindow(), WidgetItem):
                            group.append(item.GetWindow().Item)
        if len(self.Groups[self.L["GROUP_NONE"]]["PANEL"].GetChildren()) > 2:
            group.append(self.L["GROUP_NONE"])
            for sizerItem in self.Groups[self.L["GROUP_NONE"]]["PANEL"].GetSizer().GetChildren():
                window = sizerItem.GetWindow()
                if isinstance(window, WidgetItem):
                    group.append(window.Item)
        self.F.M.Groups = group
        self.F.Gadget.ClearItems()
        self.F.Gadget.AddItems(group)

    # --------------------------------------
    def AddItems(self, args):
        self.Freeze()
        group = self.NewGroup(self.L["GROUP_NONE"])
        for arg in args:
            if isinstance(arg, str):
                group = self.NewGroup(arg or self.L["GROUP_NONE"])
            else:
                self.AddItem(WidgetItem(self.Groups[group]["PANEL"], item=arg, group=group))
        if self["NEW"] is None:
            self["NEW"] = UI.Button(self.Inner, size=wx.Size(-1, 64), tag=self.L["MANAGE_NEW_GROUP"], func=(self.NewGroup, None, True), res="L", edge="D")
            self.Inner.GetSizer().Add(self["NEW"], SF_NEW)
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
                    item = [i.GetWindow() for i in self.Groups[group]["PANEL"].GetSizer().GetChildren() if getattr(i.GetWindow(), "Item", None) is arg][0]
                    item.Destroy()
        for arg in args:
            if isinstance(arg, str):
                if arg in self.Groups:
                    self.DelGroup(arg)
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
        btnAdd = UI.Button(panel, size=wx.Size(36, 36), pic=self.R["MANAGE_ADD"], func=None, edge=None, res="L")
        groupSizer.Add(btnAdd, SF_ITEM)
        btnDel = UI.Button(panel, size=wx.Size(36, 36), pic=self.R["MANAGE_DEL"], func=(self.DelGroup, title), edge=None, res="L")
        groupSizer.Add(btnDel, SF_ITEM)
        panel.SetSizer(groupSizer)
        self.Inner.GetSizer().AddMany(((title, SF_TITLE), (panel, SF_PANEL)))
        self.Groups[group] = {"TITLE": title, "PANEL": panel, "ADD": btnAdd, "DEL": btnDel}
        if self["NEW"]:
            self.Inner.GetSizer().Detach(self["NEW"])
            self.Inner.GetSizer().Add(self["NEW"], SF_NEW)
        if layout:
            self.OnArrangement()
        return group

    def DelGroup(self, title):
        group = title.group if hasattr(title, "group") else title
        if group == self.L["GROUP_NONE"]:
            return
        for child in self.Groups[group]["PANEL"].GetChildren():
            if isinstance(child, WidgetItem):
                child.ChangeGroup(self.L["GROUP_NONE"], None, False)
        sizer = self.Inner.GetSizer()
        sizer.Detach(self.Groups[group]["TITLE"])
        sizer.Detach(self.Groups[group]["PANEL"])
        self.Groups[group]["TITLE"].DestroyLater()
        self.Groups[group]["PANEL"].DestroyLater()
        del self.Groups[group]
        self.OnArrangement()

    def AddItem(self, item, index=None, layout=False):
        sizer = item.GetParent().GetSizer()
        index = sizer.GetItemCount() - 2 if index is None else min(index, sizer.GetItemCount() - 2)
        sizer.Insert(index, item, SF_ITEM)
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
class GroupTitle(UI.Button):
    def __init__(self, parent, group):
        self.group = group
        isNoGroup = group == parent.L["GROUP_NONE"]
        super().__init__(parent, size=wx.Size(-1, 20), tag=group, func=None if isNoGroup else self.ShowNameChange, edge="D")
        # DialogFrame - Main - Outer - Inner - Title
        self.Main = parent.GetGrandParent()
        if not isNoGroup:
            self.Text = UI.Text(self, style=wx.TE_CENTER | wx.SIMPLE_BORDER | wx.TE_PROCESS_ENTER)
            self.Text.SetMaxLength(24)
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
        self.Text.SelectAll()
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
        Sizer.Insert(index, self, SF_TITLE)
        Sizer.Insert(index + 1, panel, SF_PANEL)
        self.Main.OnArrangement()


# ======================================================== Item ========================================================
class WidgetItem(UI.Button):
    def __init__(self, parent, item, group):
        super().__init__(parent, size=wx.Size(108, 36), tag=("\n".join(item.NAME.split()), "L", 38), pic=(item.__RES__["BUTTON"], "L", 2), res="L", edge=None)
        self.Item = item
        # Main - Outer - Inner - Title/Panel - Item
        self.Inner = self.GetGrandParent()
        self.Main = self.Inner.GetGrandParent()
        self.group = group
        self.todo = None
        self.index = None
        self.pointing = None
        self.currentIndex = None

    def ChangeGroup(self, group=None, index=None, layout=True):
        self.group = group if group else self.Main.NewGroup()
        self.GetParent().GetSizer().Detach(self)
        self.Reparent(self.Main.Groups[self.group]["PANEL"])
        self.Main.AddItem(self, index, layout)

    def OnMouse(self, evt):
        super().OnMouse(evt)
        evtType = evt.GetEventType()
        if evtType == wx.wxEVT_LEFT_DOWN:
            self.SetCursor(self.Item.__RES__["CURSOR"])
        elif evtType == wx.wxEVT_LEFT_UP:
            UI.Do(self.todo)
            if self.pointing:
                self.pointing.Play("LEAVE")
            self.todo = None
            self.pointing = None
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
        super().__init__(parent=parent, title=parent.L["MANAGE_TITLE"], size=wx.Size(720, 480), main=Main, style=wx.FRAME_NO_TASKBAR)
        self.Head.GetSizer().Insert(0,
                                    UI.ToolNormal(self.Head, size=UI.SETTINGS["DLG_HEAD_BTN"], pics=self.R["AP_HELP"],
                                                  func=(parent.OnSimpleDialog, "MANAGE_HELP_HEAD", "MANAGE_HELP_TEXT")),
                                    0, wx.ALL, 3)
        self.Head.SetTagOffset(24, 0)
        self.Center()
        self.Layout()
        self.Play("FADEIN")


# ===================================================== Downloader =====================================================
TOY_URL = "https://github.com/yadizhou/LabPype-ToyWidget/"
BLOCK_SIZE = 1024 * 8


class Downloader(UI.BaseMain):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(480, -1))
        self.F = self.GetGrandParent()
        Sizer = wx.BoxSizer(wx.VERTICAL)
        SubSizer = wx.BoxSizer(wx.HORIZONTAL)
        self["URL"] = self.AddLineCtrl(Sizer, hint=TOY_URL, width=-1)
        self["STATUS"] = self.AddStaticText(SubSizer, width=320)
        SubSizer.Add(4, 4, 1)
        self.AddStdButton(SubSizer, onOK=self.OnOK, onCancel=self.OnClose)
        Sizer.Add(SubSizer, 0, wx.EXPAND)
        self.SetSizer(Sizer)
        self.Thread = None
        self.NewTimer("STATUS", self.OnUpdateStatus)

    def OnOK(self):
        url = self["URL"].GetValue() or TOY_URL
        if not url.endswith("/"):
            url += "/"
        url = urllib.parse.urljoin(url, "zipball/master/")
        self.StartTimer("STATUS", 50, wx.TIMER_CONTINUOUS)
        self.Thread = Thread(target=self.Download, args=(url,))
        self.Thread.start()

    def Download(self, url):
        thread = threading.currentThread()
        filepath = None
        try:
            with urllib.request.urlopen(url) as response:
                filename = response.headers["Content-Disposition"].partition("filename=")[-1]
                filepath = os.path.join(self.F.M.pathDownloaded, filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                total = response.getheader("Content-Length") or "?"
                downloaded = 0
                with open(filepath, "wb") as fo:
                    while thread.Checkpoint("%s/%s" % (downloaded, total)):
                        buffer = response.read(BLOCK_SIZE)
                        if not buffer:
                            break
                        downloaded += fo.write(buffer)
            wx.CallAfter(self.DownLoadFinish, filepath)
        except Interrupted:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            wx.CallAfter(self.F.OnSimpleDialog, "GENERAL_HEAD_FAIL", "MANAGE_REMOTE_FAIL", textData=url)

    def DownLoadFinish(self, fp):
        self.F.Manage.DoInstall(fp)
        self.OnClose()

    def OnUpdateStatus(self):
        if self.Thread.isAlive():
            self["STATUS"].SetLabel(self.Thread.status)

    def OnClose(self):
        if self.Thread and self.Thread.isAlive():
            self.Thread.stop = True
            self.Thread.join()
        self.Frame.Play("FADEOUT")
