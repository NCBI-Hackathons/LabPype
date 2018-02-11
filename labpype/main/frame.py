# -*- coding: utf-8 -*-

import io
import wx
import json
import zipfile
import DynaUI as UI
from .. import utility as Ut
from ..gui.canvas import Canvas
from ..gui.record import Record
from ..gui.gadget import Gadget
from ..gui.harbor import Harbor
from ..gui.manage import Manage
from ..gui.dialog import SimpleDialog, MakeDialog, SaveDialog, LoadDialog

__all__ = ["MainFrame"]


class MainFrame(wx.Frame):
    def __init__(self, r, s, l, m):
        super().__init__(parent=None, title=l["TITLE"], pos=s["LAST_POS"], size=s["LAST_SIZE"], style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)
        self.R = r
        self.S = s
        self.L = l
        self.M = m
        self.D = {}
        self.T = {"LAST_FILE": "", }

        self.SetStatus = UI.DoNothing
        self.SetDoubleBuffered(True)
        self.SetMinSize(wx.Size(800, 600))
        self.SetIcon(self.R["__LabPype__"])
        self.SetFont(self.R["FONT_N"])
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        if self.S["MAXIMIZED"]:
            self.Maximize()

        self.Tool = UI.Tool(self, edge=("", "B"))
        self.Info = UI.Info(self, edge=("T", ""))
        self.Gadget = Gadget(self, size=wx.Size(self.S["WIDTH_GADGET"], -1))
        self.Canvas = Canvas(self)
        self.Harbor = Harbor(self, size=wx.Size(self.S["WIDTH_HARBOR"], -1))
        self.Manage = None

        self.Center = UI.BaseControl(self, size=wx.Size(-1, self.S["HEIGHT_CENTER"]), edge=("LR", ""))
        self.Record = Record(self.Center)

        self.SashC = UI.Sash(self, target=self.Center, direction="B", vRange=(0, 250), edge=("LR", "T"))
        self.SashL = UI.Sash(self, target=self.Gadget, direction="L", vRange=(0, 384), edge=("T", "RB"))
        self.SashR = UI.Sash(self, target=self.Harbor, direction="R", vRange=(0, 600), edge=("T", "LB"))
        self.HiderC = UI.Hider(self, targets=(self.Center, self.SashC), orientation="H", edge=("LR", "B"))
        self.HiderL = UI.Hider(self, targets=(self.Gadget, self.SashL), edge="H")
        self.HiderR = UI.Hider(self, targets=(self.Harbor, self.SashR), edge="H")
        self.HiderC.SetTip(self.SetStatus, self.L["HIDER_CENTER"])
        self.HiderL.SetTip(self.SetStatus, self.L["HIDER_GADGET"])
        self.HiderR.SetTip(self.SetStatus, self.L["HIDER_HARBOR"])

        self.AcceleratorEntries = []
        for flags, keyCode, func in (
                (wx.ACCEL_NORMAL, wx.WXK_F3, self.HiderL.Click),
                (wx.ACCEL_NORMAL, wx.WXK_F4, self.HiderC.Click),
                (wx.ACCEL_NORMAL, wx.WXK_F5, self.HiderR.Click),
                (wx.ACCEL_CTRL, ord("F"), lambda evt: self.Gadget.Tool["GADGET_SEARCH"].SetFocus()),
                (wx.ACCEL_CTRL, ord("D"), self.Gadget.Tool["GADGET_CANCEL"].Click),
                (wx.ACCEL_CTRL, ord("E"), self.Gadget.Tool["TOOL_T_SHOW"].Click),
                (wx.ACCEL_CTRL, ord("R"), self.Gadget.Tool["TOOL_T_TEXT"].Click),
                (wx.ACCEL_CTRL, ord("W"), self.Gadget.Tool["TOOL_MANAGE"].Click),
                (wx.ACCEL_CTRL, ord("A"), lambda evt: self.Canvas.SelectAll()),
        ):
            cmd = wx.NewId()
            self.Bind(wx.EVT_MENU, func, id=cmd)
            self.AcceleratorEntries.append(wx.AcceleratorEntry(flags=flags, keyCode=keyCode, cmd=cmd))

        self.Tool.AddItemsWithHotKey(
            ("N", "TOOL_OPTION", self.OnOption, wx.ACCEL_CTRL | wx.ACCEL_ALT, ord("S")),
            "|",
            ("N", "TOOL_FILE_N", self.OnNew, wx.ACCEL_CTRL, ord("N")),
            ("N", "TOOL_FILE_O", (self.OnMakeDialog, "DIALOG_HEAD_LOAD", LoadDialog, {"buttons": False}), wx.ACCEL_CTRL, ord("O")),
            ("N", "TOOL_FILE_S", (self.OnMakeDialog, "DIALOG_HEAD_SAVE", SaveDialog, {"buttons": False}), wx.ACCEL_CTRL, ord("S")),
            "|",
            ("T", "TOOL_T_ANCR", (self.OnToggle, "TOGGLE_ANCR"), wx.ACCEL_NORMAL, wx.WXK_F6, {"toggle": self.S["TOGGLE_ANCR"]}),
            ("T", "TOOL_T_NAME", (self.OnToggle, "TOGGLE_NAME"), wx.ACCEL_NORMAL, wx.WXK_F7, {"toggle": self.S["TOGGLE_NAME"]}),
            ("T", "TOOL_T_SNAP", (self.OnToggle, "TOGGLE_SNAP"), wx.ACCEL_NORMAL, wx.WXK_F8, {"toggle": self.S["TOGGLE_SNAP"]}),
            ("T", "TOOL_T_CURV", self.Canvas.ToggleLinkType, wx.ACCEL_NORMAL, wx.WXK_F9, {"toggle": self.S["TOGGLE_CURV"]}),
            ("T", "TOOL_T_DIAG", self.OnToggleDialogSize, wx.ACCEL_NORMAL, wx.WXK_F10, {"toggle": 0}),
            ("T", "TOOL_T_FSCN", self.OnToggleFullScreen, wx.ACCEL_NORMAL, wx.WXK_F11, {"toggle": 0}),
            "|",
            ("N", "TOOL_ALGN_L", (self.Canvas.Align, Ut.AlignL), wx.ACCEL_CTRL, wx.WXK_NUMPAD4),
            ("N", "TOOL_ALGN_V", (self.Canvas.Align, Ut.AlignV), wx.ACCEL_CTRL, wx.WXK_NUMPAD5),
            ("N", "TOOL_ALGN_R", (self.Canvas.Align, Ut.AlignR), wx.ACCEL_CTRL, wx.WXK_NUMPAD6),
            ("N", "TOOL_ALGN_T", (self.Canvas.Align, Ut.AlignT), wx.ACCEL_CTRL, wx.WXK_NUMPAD8),
            ("N", "TOOL_ALGN_H", (self.Canvas.Align, Ut.AlignH), wx.ACCEL_CTRL, wx.WXK_NUMPAD0),
            ("N", "TOOL_ALGN_B", (self.Canvas.Align, Ut.AlignB), wx.ACCEL_CTRL, wx.WXK_NUMPAD2),
            "|",
            ("N", "TOOL_DIST_H", (self.Canvas.Distribute, Ut.DistributeH), wx.ACCEL_CTRL, ord("H")),
            ("N", "TOOL_DIST_V", (self.Canvas.Distribute, Ut.DistributeV), wx.ACCEL_CTRL, ord("V")),
            "|",
            ("N", "TOOL_MOVE_T", (self.Canvas.AlterLayer, "T"), wx.ACCEL_CTRL, wx.WXK_NUMPAD9),
            ("N", "TOOL_MOVE_U", (self.Canvas.AlterLayer, "U"), wx.ACCEL_CTRL, wx.WXK_NUMPAD7),
            ("N", "TOOL_MOVE_D", (self.Canvas.AlterLayer, "D"), wx.ACCEL_CTRL, wx.WXK_NUMPAD1),
            ("N", "TOOL_MOVE_B", (self.Canvas.AlterLayer, "B"), wx.ACCEL_CTRL, wx.WXK_NUMPAD3),
            "|",
            ("N", "TOOL_CANCEL", self.OnDismissAllDialog, wx.ACCEL_CTRL, wx.WXK_DELETE, {"res": "R"}),
            ("N", "TOOL_DELETE", self.Canvas.DeleteSelected, wx.ACCEL_NORMAL, wx.WXK_DELETE, {"res": "R"}),
        )
        self.Info.AddItems((wx.StaticText(self.Info, size=(268, 16)), 0),
                           (wx.StaticText(self.Info, size=(-1, 16)), 1),
                           (wx.StaticText(self.Info, size=(268, 16)), 0))

        self.SetAcceleratorTable(wx.AcceleratorTable(self.AcceleratorEntries))

        CenterSizer = wx.BoxSizer(wx.HORIZONTAL)
        CenterSizer.Add(self.Record, 1, wx.EXPAND | wx.ALL, 1)
        self.Center.SetSizer(CenterSizer)

        MiddleSizer = wx.BoxSizer(wx.VERTICAL)
        MiddleSizer.AddMany((
            (self.Canvas, 1, wx.EXPAND),
            (self.SashC, 0, wx.EXPAND),
            (self.Center, 0, wx.EXPAND),
            (self.HiderC, 0, wx.EXPAND),))
        MainSizer = wx.BoxSizer(wx.HORIZONTAL)
        MainSizer.AddMany((
            (self.HiderL, 0, wx.EXPAND),
            (self.Gadget, 0, wx.EXPAND),
            (self.SashL, 0, wx.EXPAND),
            (MiddleSizer, 1, wx.EXPAND),
            (self.SashR, 0, wx.EXPAND),
            (self.Harbor, 0, wx.EXPAND),
            (self.HiderR, 0, wx.EXPAND),))
        FrameSizer = wx.BoxSizer(wx.VERTICAL)
        FrameSizer.AddMany((
            (self.Tool, 0, wx.EXPAND),
            (MainSizer, 1, wx.EXPAND),
            (self.Info, 0, wx.EXPAND),))
        self.SetSizer(FrameSizer)
        self.Layout()
        if not self.S["SHOW_GADGET"]:
            self.HiderL.OnHider()
        if not self.S["SHOW_HARBOR"]:
            self.HiderR.OnHider()
        if not self.S["SHOW_CENTER"]:
            self.HiderC.OnHider()

        self.M.Init(self)

    # --------------------------------------
    def OnToggle(self, key):
        self.S[key] = not self.S[key]
        self.Canvas.ReDraw()

    def OnBundle(self, key, value):
        self.S[key] = value
        self.Canvas.ReDraw()

    def OnToggleFullScreen(self):
        self.ShowFullScreen(not self.IsFullScreen())

    def OnToggleDialogSize(self):
        t = self.Tool["TOOL_T_DIAG"].IsToggled()
        for w in self.Canvas.Widget:
            if w.Dialog:
                if w.Dialog.detached:
                    if t != bool(w.Dialog.Frame.minimized):
                        w.Dialog.Frame.OnMinimize()
                else:
                    if t == w.Dialog.IsShown():
                        self.Harbor.OnChild(w.Dialog)

    def OnDismissAllDialog(self):
        for w in self.Canvas.Widget:
            if w.Dialog and w.Dialog.detached:
                w.Dialog.Frame.OnClose()

    # --------------------------------------
    def OnSimpleDialog(self, titleKey, textKey, titleData=None, textData=None, onOK=None, unique=False):
        title = self.L.Get(titleKey) if titleData is None else (self.L.Get(titleKey) % titleData)
        text = self.L.Get(textKey) if textData is None else (self.L.Get(textKey) % textData)
        if unique:
            if self.D.get(textKey):
                self.D[textKey].SetFocus()
            else:
                self.D[textKey] = SimpleDialog(self, title, text, onOK)
        else:
            SimpleDialog(self, title, text, onOK)

    def OnMakeDialog(self, titleKey, main, head=None, unique=True):
        title = self.L[titleKey]
        if unique:
            if self.D.get(titleKey):
                self.D[titleKey].SetFocus()
            else:
                self.D[titleKey] = MakeDialog(self, title, main, head)
        else:
            MakeDialog(self, title, main, head)

    def OnShowManage(self):
        if self.Manage:
            self.Manage.SetFocus()
        else:
            self.Manage = Manage(self).Main

    # --------------------------------------
    def OnNew(self):
        if self.Canvas.Widget:
            self.OnSimpleDialog("DIALOG_HEAD_NEW?", "DIALOG_NEW?_INFO", onOK=self.OnClear, unique=True)
        else:
            self.OnClear()

    def OnClear(self):
        self.Canvas.ClearWidget()
        self.Record.ClearAll()
        self.T["LAST_FILE"] = ""

    def GetScheme(self):
        return {w.Id: (w.__ID__, w.UUID, w.GetPosition(), w.SaveState(),
                       [a.Id for a in w.Anchors],
                       [[i.Id for i in a.connected] for a in w.Incoming],
                       w.SaveMeta())
                for w in self.Canvas.Widget}

    def SetScheme(self, data, schemeOnly):
        widgets = {}
        anchors = {}
        for wId in data:
            widgets[wId] = self.Canvas.AddWidget(self.M.Widgets[data[wId][0]], data[wId][2])
            for aId, anchor in zip(data[wId][4], widgets[wId].Anchors):
                anchors[aId] = anchor
        for wId in data:
            for connected, anchor in zip(data[wId][5], widgets[wId].Incoming):
                for aId in connected:
                    anchors[aId].SetTarget(anchor, False)
        if not schemeOnly:
            for wId in data:
                widgets[wId].UUID = data[wId][1]
                widgets[wId].LoadState(data[wId][3])
                widgets[wId].LoadMeta(data[wId][6])
        return widgets

    def OnSave(self, fp):
        schemeOnly = fp.lower().endswith(".pas")
        try:
            with zipfile.ZipFile(fp, "w") as z:
                z.writestr("_", json.dumps(self.GetScheme()))  # scheme -> str -> utf-8 -> b
                if not schemeOnly:
                    for w in self.Canvas.Widget:
                        z.writestr(str(w.Id), w.SaveData())  # widget.SaveData -> str or b, str -> utf-8 -> b, b -> b
                for f in z.filelist:
                    f.create_system = 0
            self.NewHistory(fp)
            return True
        except Exception as e:
            self.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_SAVE_FILE_FAILED", textData=str(e))
            return False

    def OnLoad(self, fp, append, schemeOnly):
        self.Canvas.Freeze()
        if fp.lower().endswith(".pas"):
            schemeOnly = True
        try:
            with zipfile.ZipFile(fp, "r") as z:
                with z.open("_") as f:
                    data = json.load(io.TextIOWrapper(f, "utf-8"))  # b -> utf-8 -> str -> scheme
                if len(data) + (len(self.Canvas.Widget) if append else 0) > 255:
                    self.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_TOO_MANY_WIDGETS")
                    return False
                for wId in data:
                    if data[wId][0] not in self.M.Widgets:
                        self.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_UNKNOWN_WIDGET", textData=data[wId][0])
                        return False
                    if append and self.M.Widgets[data[wId][0]].UNIQUE and self.M.Widgets[data[wId][0]].__INSTANCE__:
                        self.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_SINGLETON_EXIST", textData=data[wId][0])
                        return False
                if not append:
                    self.OnClear()
                widgets = self.SetScheme(data, schemeOnly=schemeOnly)
                if not schemeOnly:
                    for wId in z.namelist():
                        if wId != "_":
                            with z.open(wId) as f:
                                widgets[wId].LoadData(f)  # b -> widget.LoadData
                for wId in widgets:
                    widgets[wId].UpdateIncoming()
                    widgets[wId].PositionAnchor()
                    widgets[wId].SetName()
            self.NewHistory(fp)
            return True
        except Exception as e:
            self.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_LOAD_FILE_FAILED", textData=str(e))
            return False
        finally:
            self.Canvas.Thaw()

    def NewHistory(self, fp):
        key = "HISTORY_SCHEME" if fp.lower().endswith(".pas") else "HISTORY_PROJECT"
        if fp in self.S[key]:
            self.S[key].remove(fp)
        self.S[key].insert(0, fp)
        self.S[key] = self.S[key][:8]
        self.T["LAST_FILE"] = fp

    # --------------------------------------
    def OnOption(self):
        pass  # TODO

    # --------------------------------------
    def OnClose(self, evt):
        app = wx.GetApp()
        if hasattr(app, "_CallAfterId"):
            app.Disconnect(-1, -1, app._CallAfterId)
        for w in self.Canvas.Widget:
            w.StopThread()
        for dialog in wx.GetTopLevelWindows():
            if isinstance(dialog, UI.BaseDialog):
                dialog.Destroy()
        if not self.IsMaximized():
            self.S["LAST_SIZE"] = tuple(self.GetSize())
            self.S["LAST_POS"] = tuple(self.GetPosition())
        self.S["MAXIMIZED"] = self.IsMaximized()
        self.S["SHOW_GADGET"] = self.Gadget.IsShown()
        self.S["SHOW_HARBOR"] = self.Harbor.IsShown()
        self.S["SHOW_CENTER"] = self.Center.IsShown()
        self.S["WIDTH_GADGET"] = self.Gadget.GetSize()[0]
        self.S["WIDTH_HARBOR"] = self.Harbor.GetSize()[0]
        self.S["HEIGHT_CENTER"] = self.Center.GetSize()[1]
        self.S.Save()
        self.M.Save()
        evt.Skip()
