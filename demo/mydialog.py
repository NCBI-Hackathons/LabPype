# -*- coding: utf-8 -*-


from expcatalyst.widget import Dialog


class Number(Dialog):
    def Initialize(self, Sizer):
        self["OUT"] = self.AddLineCtrl(Sizer, "The result is:", "")

    def GetData(self):
        if self.Widget["OUT"] is not None:
            self["OUT"].SetValue(str(self.Widget["OUT"]))
        else:
            self["OUT"].SetValue("")
