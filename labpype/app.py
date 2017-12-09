# -*- coding: utf-8 -*-

import os
import wx
import DynaUI as UI
from . import utility as Ut
from .main.frame import MainFrame
from .main.resource import Resource
from .main.setting import Setting
from .main.locale import Locale
from .main.manager import Manager

__all__ = ["App"]


class App(wx.App):
    def __init__(self, path=None):
        super().__init__(redirect=0, useBestVisual=True)
        self.path = path or os.path.join(wx.GetHomeDir(), ".labpype")

    def Start(self):
        m = Manager(self.path)
        r = Resource(os.path.join(self.path, "resources.json"))
        s = Setting(os.path.join(self.path, "settings.json"))
        l = Locale(Ut.Find("lang", "%s.json" % s["LANGUAGE"]))
        if not (m.ok and r.ok and s.ok and l.ok):
            return UI.ShowSimpleMessageDialog(None, l["MSG_WORKSPACE_FAIL"] % self.path, l["GENERAL_HEAD_FAIL"])
        Frame = MainFrame(r, s, l, m)
        Frame.Show()
        self.MainLoop()
