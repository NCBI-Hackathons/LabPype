# -*- coding: utf-8 -*-

import wx
from wx import stc


# ======================================================= Record =======================================================
class Record(stc.StyledTextCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.R = parent.R
        self.SetUseVerticalScrollBar(False)
        self.SetUseHorizontalScrollBar(False)
        self.SetCaretWidth(2)
        self.SetMarginWidth(1, 0)
        self.SetSelBackground(True, self.R["COLOR_BG_B"])
        self.StyleSetBackground(stc.STC_STYLE_DEFAULT, self.R["COLOR_BG_L"])
        self.StyleSetForeground(stc.STC_STYLE_DEFAULT, self.R["COLOR_FG_L"])
        self.StyleClearAll()
        self.StyleSetSpec(1, "fore:%s" % self.R["COLOR_R"])
        self.StyleSetSpec(2, "fore:%s" % self.R["COLOR_FG_L"])
        self.SetReadOnly(True)
        self.minimized = False

    def ClearAll(self):
        self.SetReadOnly(False)
        super().ClearAll()
        self.SetReadOnly(True)

    def LogErr(self, text):
        self.SetReadOnly(False)
        self.StartStyling(self.GetLastPosition(), 0xff)
        self.AppendText(text + "\n")
        self.SetStyling(len(text), 1)
        self.SetReadOnly(True)
        self.ScrollToEnd()

    def LogOut(self, text):
        self.SetReadOnly(False)
        self.StartStyling(self.GetLastPosition(), 0xff)
        self.AppendText(text + "\n")
        self.SetStyling(len(text), 2)
        self.SetReadOnly(True)
        self.ScrollToEnd()

    def Minimize(self):
        if self.minimized:
            self.SetInitialSize(wx.Size(-1, self.minimized))
            self.minimized = False
        else:
            self.minimized = self.GetSize()[1]
            self.SetInitialSize(wx.Size(-1, 0))
        self.GetParent().Layout()
