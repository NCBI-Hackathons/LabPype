# -*- coding: utf-8 -*-


import os
import wx
import DynaUI as UI


# ======================================================= Maker ========================================================
def ShowSimpleText(parent, title, text):
    Dialog = UI.BaseDialog(parent, title=title, style=wx.STAY_ON_TOP, head={"buttons": False})
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(wx.StaticText(Dialog.Main, label=text), 1, wx.EXPAND | wx.ALL, 8)
    Dialog.Main.SetSizer(sizer)
    Dialog.SetSize(Dialog.GetEffectiveMinSize())
    Dialog.Layout()
    Dialog.Center()
    Dialog.Play("FADEIN")
    return Dialog


def MakeDialog(parent, title, main, head=None):
    Dialog = UI.BaseDialog(parent=parent, title=title, style=wx.STAY_ON_TOP, main=main, head=head or {})
    Dialog.SetSize(Dialog.GetEffectiveMinSize())
    Dialog.CenterOnParent()
    Dialog.Play("FADEIN")
    return Dialog


# ======================================================== New =========================================================
class NewConfirm(UI.BaseMain):
    def __init__(self, parent):
        super().__init__(parent)
        self.MainFrame = self.GetGrandParent()
        self.MainFrame.Disable()
        self.GetParent().OnClose = self.OnClose
        Sizer = wx.BoxSizer(wx.VERTICAL)
        self.AddStaticText(Sizer, value=self.L["DIALOG_NEW?_INFO"])
        self.AddStdButton(Sizer, onOK=(self.OnConfirm, True), onCancel=(self.OnConfirm, False))
        self.SetSizer(Sizer)

    def OnClose(self):
        self.MainFrame.Enable()
        self.MainFrame.Tool["TOOL_FILE_N"].Play("LEAVE_WHEN_CLICKED")
        self.GetParent().Play("FADEOUT")

    def OnConfirm(self, clear):
        self.GetParent().OnClose()
        if clear:
            self.MainFrame.OnClear()


# ======================================================== Save ========================================================
class SaveDialog(UI.BaseMain):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(480, -1))
        self.MainFrame = self.GetGrandParent()
        Sizer = wx.BoxSizer(wx.VERTICAL)
        SubSizer = wx.BoxSizer(wx.HORIZONTAL)
        self["FILE"] = self.AddFilePicker(Sizer, mode="S", value=self.MainFrame.T["LAST_FILE"], wildcard="All files (*.pa,*.pas)|*.pa;*.pas|Project files (*.pa)|*.pa|Scheme files (*.pas)|*.pas", onSelect=self.OnChooseFile)
        self.AddSeparator(Sizer)
        Sizer.Add(SubSizer, 1, wx.EXPAND)
        self["MODE"] = self.AddButtonBundle(SubSizer, tags=(self.L["DIALOG_SAVE_MODE_S"], self.L["DIALOG_SAVE_MODE_P"]), group="_SAVE_MODE_", width=100, toggled=self.MainFrame.T["LAST_FILE"].lower().endswith(".pa"), onClick=self.OnMode)
        SubSizer.Add(4, 4, 1)
        self.AddStdButton(SubSizer, onOK=self.OnSave, onCancel=self.GetParent().OnClose)
        self.SetSizer(Sizer)

    def OnMode(self):
        if self["FILE"].GetValue().lower().endswith(".pa") and self["MODE"].GetToggled() == 0:
            self["FILE"].SetValue(self["FILE"].GetValue()[:-2] + "pas")
        elif self["FILE"].GetValue().lower().endswith(".pas") and self["MODE"].GetToggled() == 1:
            self["FILE"].SetValue(self["FILE"].GetValue()[:-1])

    def OnChooseFile(self):
        if self["FILE"].GetValue().lower().endswith(".pa"):
            self["MODE"].SetToggled(1)
        elif self["FILE"].GetValue().lower().endswith(".pas"):
            self["MODE"].SetToggled(0)

    def OnSave(self):
        if self.MainFrame.OnSave(self["FILE"].GetValue()):
            return self.GetParent().OnClose()
        wx.Bell()


# ======================================================== Load ========================================================
class LoadDialog(UI.BaseMain):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(480, 400))
        self.MainFrame = self.GetGrandParent()
        Sizer = wx.BoxSizer(wx.VERTICAL)
        SubSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        SubSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        Sizer.Add(SubSizer1, 1, wx.EXPAND)
        self["LB_S"] = self.AddListBox(SubSizer1, label=self.L["DIALOG_LOAD_LIST_S"], choices=["\n".join(os.path.split(i)) for i in self.S["HISTORY_SCHEME"]], inline=False, onClick=(self.OnSelectRecent, "LB_S"))
        self["LB_P"] = self.AddListBox(SubSizer1, label=self.L["DIALOG_LOAD_LIST_P"], choices=["\n".join(os.path.split(i)) for i in self.S["HISTORY_PROJECT"]], inline=False, onClick=(self.OnSelectRecent, "LB_P"))
        self["FILE"] = self.AddFilePicker(Sizer, mode="L", onSelect=self.OnChooseFile, wildcard="All files (*.pa,*.pas)|*.pa;*.pas|Project files (*.pa)|*.pa|Scheme files (*.pas)|*.pas")
        self.AddSeparator(Sizer)
        Sizer.Add(SubSizer2, 0, wx.EXPAND)
        self["MODE"] = self.AddButtonBundle(SubSizer2, tags=(self.L["DIALOG_LOAD_MODE_A"], self.L["DIALOG_LOAD_MODE_O"]), toggled=0, group="_OPEN_MODE_", width=80)
        SubSizer2.Add(4, 4, 1)
        self["ONLY"] = self.AddButtonToggle(SubSizer2, tags=(self.L["DIALOG_LOAD_ONLY_N"], self.L["DIALOG_LOAD_ONLY_Y"]), toggle=False, width=160)
        SubSizer2.Add(4, 4, 1)
        self.AddStdButton(SubSizer2, onOK=self.OnLoad, onCancel=self.GetParent().OnClose)
        self.SetSizer(Sizer)
        self["LB_S"].SetLineHeight(32)
        self["LB_P"].SetLineHeight(32)
        self["MODE"][1].ChangeResources("R")

    def OnChooseFile(self):
        if self["FILE"].GetValue().lower().endswith(".pa") and self["ONLY"].IsToggled():
            self["ONLY"].Click()
        elif self["FILE"].GetValue().lower().endswith(".pas") and not self["ONLY"].IsToggled():
            self["ONLY"].Click()

    def OnSelectRecent(self, activated):
        inactivated = "LB_S" if activated != "LB_S" else "LB_P"
        self[inactivated].SetSelection(-1)
        self[inactivated].ReDraw()
        if self[activated].HasSelection():
            self["FILE"].SetValue(os.path.join(*self[activated].GetStringSelection().split("\n")))
            self.OnChooseFile()

    def OnLoad(self):
        if self.MainFrame.OnLoad(self["FILE"].GetValue(), append=self["MODE"].GetToggled() == 0, schemeOnly=self["ONLY"].IsToggled()):
            return self.GetParent().OnClose()
        wx.Bell()
