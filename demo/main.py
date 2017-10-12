# -*- coding: utf-8 -*-


import os
import wx
import expcatalyst
from expcatalyst.builtin import FlowControl, Number
import mywidget as Wi

MAIN_PATH = os.path.dirname(os.path.realpath(__file__))
Here = lambda f="": os.path.join(MAIN_PATH, f)

WIDGET_LIST = FlowControl + Number + \
              ["Math",
               ("#80ccff", Wi.Summer,),
               ("#ff9fff", Wi.Multiplier,),
               ]

App = wx.App(redirect=0, useBestVisual=True)

settingFile = Here("settings.json")
if not os.path.exists(settingFile):
    with open(settingFile, "w", encoding="utf-8") as f:
        f.write("\x7b\x7d")

R = expcatalyst.Resource()
S = expcatalyst.Setting()
L = expcatalyst.Locale()
S.Load(settingFile)

Frame = expcatalyst.MainFrame(R, S, L, WIDGET_LIST)
Frame.Show()
App.MainLoop()
