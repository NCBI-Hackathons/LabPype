# -*- coding: utf-8 -*-

import os
import wx
import DynaUI as UI


# ======================================================= Maker ========================================================
def SimpleDialog(parent, title, text, onOK=None):
    Dialog = UI.BaseDialog(parent=parent, title=title, head={"buttons": False}, style=wx.FRAME_NO_TASKBAR)
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(wx.StaticText(Dialog.Main, label=text), 1, wx.EXPAND | wx.ALL, 8)
    if onOK:
        Dialog.Main.AddStdButton(sizer, onOK=((UI.DoNothing,), onOK, Dialog.OnClose), onCancel=Dialog.OnClose)
    else:
        Dialog.Main.AddStdButton(sizer, onOK=Dialog.OnClose)
    Dialog.Main.SetSizer(sizer)
    x, y = Dialog.GetEffectiveMinSize()
    Dialog.SetSize((max(x, 120), max(y, UI.SETTINGS["DLG_HEAD"] + 10)))
    Dialog.Layout()
    Dialog.Center()
    Dialog.Play("FADEIN")
    return Dialog


def MakeDialog(parent, title, main, head=None):
    Dialog = UI.BaseDialog(parent=parent, title=title, main=main, head=head or {}, style=wx.FRAME_NO_TASKBAR)
    x, y = Dialog.GetEffectiveMinSize()
    Dialog.SetSize((max(x, 120), max(y, UI.SETTINGS["DLG_HEAD"] + 10)))
    Dialog.CenterOnParent()
    Dialog.Play("FADEIN")
    return Dialog


# ======================================================== Save ========================================================
class SaveDialog(UI.BaseMain):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(480, -1))
        self.F = parent.GetParent()
        Sizer = wx.BoxSizer(wx.VERTICAL)
        SubSizer = wx.BoxSizer(wx.HORIZONTAL)
        self["FILE"] = self.AddPickerFile(Sizer, mode="S", value=self.F.T["LAST_FILE"],
                                          wildcard="All files (*.pa,*.pas)|*.pa;*.pas|Project files (*.pa)|*.pa|Scheme files (*.pas)|*.pas", onSelect=self.OnChooseFile)
        Sizer.Add(SubSizer, 1, wx.EXPAND)
        self["MODE"] = self.AddButtonBundle(SubSizer, choices=(self.L["DIALOG_SAVE_MODE_S"], self.L["DIALOG_SAVE_MODE_P"]),
                                            width=100, selected=self.F.T["LAST_FILE"].lower().endswith(".pa"), onClick=self.OnMode)
        SubSizer.Add(4, 4, 1)
        self.AddStdButton(SubSizer, onOK=self.OnSave, onCancel=self.Frame.OnClose)
        self.SetSizer(Sizer)

    def OnMode(self):
        if self["FILE"].GetValue().lower().endswith(".pa") and self["MODE"].GetSelection() == 0:
            self["FILE"].SetValue(self["FILE"].GetValue()[:-2] + "pas")
        elif self["FILE"].GetValue().lower().endswith(".pas") and self["MODE"].GetSelection() == 1:
            self["FILE"].SetValue(self["FILE"].GetValue()[:-1])

    def OnChooseFile(self):
        if self["FILE"].GetValue().lower().endswith(".pa"):
            self["MODE"].SetSelection(1)
        elif self["FILE"].GetValue().lower().endswith(".pas"):
            self["MODE"].SetSelection(0)

    def OnSave(self):
        fp = self["FILE"].GetValue()
        if fp.lower().endswith(".pa") or fp.lower().endswith(".pas"):
            if self.F.OnSave(fp):
                return self.Frame.OnClose()
        wx.Bell()


# ======================================================== Load ========================================================
class LoadDialog(UI.BaseMain):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(480, 400))
        self.F = parent.GetParent()
        Sizer = wx.BoxSizer(wx.VERTICAL)
        SubSizer0 = wx.BoxSizer(wx.HORIZONTAL)
        SubSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        SubSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        Sizer.Add(SubSizer0, 0, wx.EXPAND)
        Sizer.Add(SubSizer1, 1, wx.EXPAND)
        self.AddButton(SubSizer0, label=self.L["DIALOG_LOAD_LIST_S"], tag=self.L["DIALOG_CLEAN_S"], width=-1, onClick=(self.OnCleanRecent, "S"))
        self.AddButton(SubSizer0, label=self.L["DIALOG_LOAD_LIST_P"], tag=self.L["DIALOG_CLEAN_P"], width=-1, onClick=(self.OnCleanRecent, "P"))
        self["LB_S"] = self.AddListBox(SubSizer1, choices=["\n".join(os.path.split(i)) for i in self.S["HISTORY_SCHEME"]],
                                       onClick=(self.OnRecent, "LB_S"), onDClick=(self.OnRecentGo, "LB_S"))
        self["LB_P"] = self.AddListBox(SubSizer1, choices=["\n".join(os.path.split(i)) for i in self.S["HISTORY_PROJECT"]],
                                       onClick=(self.OnRecent, "LB_P"), onDClick=(self.OnRecentGo, "LB_P"))
        self["FILE"] = self.AddPickerFile(Sizer, mode="L", onSelect=self.OnChooseFile,
                                          wildcard="All files (*.pa,*.pas)|*.pa;*.pas|Project files (*.pa)|*.pa|Scheme files (*.pas)|*.pas")
        self.AddSeparator(Sizer)
        Sizer.Add(SubSizer2, 0, wx.EXPAND)
        self["MODE"] = self.AddButtonBundle(SubSizer2, choices=(self.L["DIALOG_LOAD_MODE_A"], self.L["DIALOG_LOAD_MODE_O"]), selected=0, width=80)
        self["ONLY"] = self.AddButtonToggle(SubSizer2, tags=(self.L["DIALOG_LOAD_ONLY_N"], self.L["DIALOG_LOAD_ONLY_Y"]), toggle=False, width=160)
        SubSizer2.Add(4, 4, 1)
        self.AddStdButton(SubSizer2, onOK=self.OnLoad, onCancel=self.Frame.OnClose)
        self.SetSizer(Sizer)
        self["LB_S"].SetLineHeight()
        self["LB_P"].SetLineHeight()
        self["LB_S"].SetLineHeight(self["LB_S"].LineHeight * 2)
        self["LB_P"].SetLineHeight(self["LB_P"].LineHeight * 2)
        self["MODE"][1].SetRes("R")

    def OnChooseFile(self):
        if self["FILE"].GetValue().lower().endswith(".pa") and self["ONLY"].IsToggled():
            self["ONLY"].Click()
        elif self["FILE"].GetValue().lower().endswith(".pas") and not self["ONLY"].IsToggled():
            self["ONLY"].Click()

    def OnRecent(self, activated):
        inactivated = "LB_S" if activated != "LB_S" else "LB_P"
        self[inactivated].SetSelection(-1)
        self[inactivated].ReDraw()
        if self[activated].HasSelection():
            self["FILE"].SetValue(os.path.join(*self[activated].GetStringSelection().split("\n")))
            self.OnChooseFile()

    def OnRecentGo(self, activated):
        self.OnRecent(activated)
        self.OnLoad()

    def OnLoad(self):
        if self["FILE"].GetValue():
            if self.F.OnLoad(self["FILE"].GetValue(), append=self["MODE"].GetSelection() == 0, schemeOnly=self["ONLY"].IsToggled()):
                return self.Frame.OnClose()
        wx.Bell()

    def OnCleanRecent(self, x):
        if x == "S":
            self.S["HISTORY_SCHEME"] = []
            self["LB_S"].SetData(())
            self["LB_S"].ReDraw()
        else:
            self.S["HISTORY_PROJECT"] = []
            self["LB_P"].SetData(())
            self["LB_P"].ReDraw()
