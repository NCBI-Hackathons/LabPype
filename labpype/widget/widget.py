# -*- coding: utf-8 -*-

import io
import wx
import math
import json
import threading
from DynaUI import GetMultiLineTextExtent, DoNothing
from ..utility import Thread, Interrupted
from .dialog import MakeWidgetDialog, Dialog
from .base import Base
from .field import BaseField
from .anchor import Anchor

__all__ = [
    "BaseWidget",
    "Widget",
    "Synced",
]


# ======================================================== Misc ========================================================
def Synced(func):
    def SyncedFunc(self, *args, **kwargs):
        if self.THREAD:
            with self.Canvas.Lock:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)

    return SyncedFunc


# ===================================================== BaseWidget =====================================================
class BaseWidget(Base):
    NAME = ""
    DESC = ""
    UNIQUE = False
    DIALOG = None
    THREAD = False
    INTERNAL = None
    INCOMING = None
    PROVIDER = None
    OUTGOING = None

    __TYPE__ = "WIDGET"
    __INITIALIZED__ = False
    __STATES__ = None
    __ID__ = None
    __RES__ = None
    __ICON__ = None
    __COLOR__ = None
    __INSTANCE__ = None
    __RECEIVER__ = None

    def __new__(cls, *args, **kwargs):
        if not cls.__INITIALIZED__:
            if cls.UNIQUE:
                if cls.__RECEIVER__ is None:
                    cls.__RECEIVER__ = []
            else:
                cls.__INSTANCE__ = []
            if cls.DIALOG in ("H", "V"):
                cls.DIALOG = type("_AutoDialog" + cls.__name__, (Dialog,), {"ORIENTATION": cls.DIALOG})
            elif isinstance(cls.DIALOG, dict):
                cls.DIALOG = type("_AutoDialog" + cls.__name__, (Dialog,), cls.DIALOG)
            if cls.INTERNAL is None:
                cls.INTERNAL = ()
            elif not isinstance(cls.INTERNAL, (tuple, list)):
                cls.INTERNAL = (cls.INTERNAL,)
            if cls.INCOMING is None:
                cls.INCOMING = ()
            elif not isinstance(cls.INCOMING[0], (tuple, list)):
                cls.INCOMING = (cls.INCOMING,)
            if cls.PROVIDER is None:
                cls.PROVIDER = ()
            elif not isinstance(cls.PROVIDER[0], (tuple, list)):
                cls.PROVIDER = (cls.PROVIDER,)
            if cls.OUTGOING is None:
                pass
            elif not isinstance(cls.OUTGOING, (tuple, list)):
                cls.OUTGOING = (cls.OUTGOING, "Output", None)
            for kls, key in cls.PROVIDER:
                if kls.__RECEIVER__ is None:
                    kls.__RECEIVER__ = []
            cls.__INITIALIZED__ = True
        return super().__new__(cls)

    def __init__(self, canvas):
        super().__init__(w=70, h=70)
        self.Canvas = canvas
        onEnter = {state: getattr(self, "OnEnter%s" % state, DoNothing) for state in self.__STATES__}
        onLeave = {state: getattr(self, "OnLeave%s" % state, DoNothing) for state in self.__STATES__}
        self.OnEnter = lambda s: onEnter[s]()
        self.OnLeave = lambda s: onLeave[s]()
        self.Bitmap = None
        self.name = None
        self.namePos = None
        self.nameSize = None
        self.Dialog = None
        self.DialogPos = None
        self.DialogSize = None
        self.Thread = None
        self.Data = {"OUT": None}
        self.Incoming = []
        self.Outgoing = []
        self.Key2Anchor = {}
        self.Pos2Anchor = {"L": {}, "T": {}, "R": {}, "B": {}}
        for field in self.INTERNAL:
            self.Data[field.key if isinstance(field, BaseField) else field] = None
        for args in self.INCOMING:
            self.AddAnchor(False, *args)
        for cls, key in self.PROVIDER:
            cls.__RECEIVER__.append(self)
            self.Data[key] = cls.__INSTANCE__ and cls.__INSTANCE__["OUT"]
        if self.OUTGOING:
            self.AddAnchor(True, self.OUTGOING[0], "OUT", True, "RBT", *self.OUTGOING[1:])
        self.Anchors = self.Incoming + self.Outgoing
        if self.__class__.UNIQUE:
            self.__class__.__INSTANCE__ = self
            for w in self.__RECEIVER__:
                w.OnAlter()
        else:
            self.__class__.__INSTANCE__.append(self)
        self.state = self.__STATES__[0]
        self.OnEnter(self.state)
        self.SetName()
        self.Init()

    # -------------------------------------------------------- #
    @Synced
    def Destroy(self):
        self.Exit()
        self.SetState = DoNothing
        self.OnLeave(self.state)
        if self.Dialog:
            self.Dialog.GetData = DoNothing
            self.Dialog.OnClose()
        self.StopThread()
        for cls, key in self.PROVIDER:
            cls.__RECEIVER__.remove(self)
        if self.__class__.UNIQUE:
            self.__class__.__INSTANCE__ = None
            for w in self.__RECEIVER__:
                w.OnAlter()
        else:
            self.__class__.__INSTANCE__.remove(self)
        for a in reversed(self.Anchors):
            a.EmptyTarget(a.send)
            a.ReleaseID()
        self.ReleaseID()
        self.Data = None

    @Synced
    def IsState(self, *states):
        return self.state in states

    @Synced
    def SetState(self, state):
        self.OnLeave(self.state)
        self.state = state
        self.OnEnter(self.state)
        wx.CallAfter(self.SetName)
        wx.CallAfter(self.Canvas.ReDraw)

    # -------------------------------------------------------- #
    def __setitem__(self, key, value):
        self.Data[key] = value

    def __getitem__(self, item):
        return self.Data[item]

    def AddAnchor(self, send, aType, key, multiple, pos, name="", anchor=None):
        a = (anchor or Anchor)(self, aType, key, multiple, send, pos, self.Canvas.L.Get(name, "ANCHOR_NAME_"))
        (self.Outgoing if send else self.Incoming).append(a)
        self.Data[key] = None
        self.Key2Anchor[key] = a
        self.Pos2Anchor[a.pos][a] = 0

    def SetName(self):
        try:
            name = self.Name()
        except Exception:
            name = self.NAME
        self.name = self.NAME if name is None else name
        self.nameSize = GetMultiLineTextExtent(self.Canvas, self.name)
        self.PositionName()

    def NewPosition(self, x, y):
        if self.Canvas.S["TOGGLE_SNAP"]:
            x = x >> 5 << 5
            y = y >> 5 << 5
        self.x = x
        self.y = y
        self.rect.SetPosition((x - 6, y - 6))
        self.PositionAnchor()
        self.PositionName()

    def PositionAnchor(self):
        for a in self.Anchors:
            del self.Pos2Anchor[a.pos][a]
            if a.connected:
                theta = math.atan2(sum(i.y for i in a.connected) / len(a.connected) - self.y - 26,
                                   sum(i.x for i in a.connected) / len(a.connected) - self.x - 26)
                index = math.ceil(theta * 4 / math.pi)
                a.pos = a.posTable[index]
            else:
                theta = 0
                a.pos = a.posAllowed[0]
            self.Pos2Anchor[a.pos][a] = theta if a.pos != "B" else -theta
        for p in "LTRB":
            n = 1 - len(self.Pos2Anchor[p])
            for index, a in enumerate(sorted(self.Pos2Anchor[p].items(), key=lambda x: x[1])):
                self._PositionAnchor(a[0], index * 18 + n * 9)

    def _PositionAnchor(self, a, offset):
        if a.pos == "L":
            ax = -6
        elif a.pos == "R":
            ax = 58
        else:
            ax = 26 + offset
        if a.pos == "T":
            ay = -6
        elif a.pos == "B":
            ay = 58
        else:
            ay = 26 + offset
        a.SetPosition(self.x + ax, self.y + ay)

    def PositionName(self):
        self.namePos = self.x + 28 - self.nameSize[0] // 2, self.y - self.nameSize[1] - 8 if self.Pos2Anchor["B"] and not self.Pos2Anchor["T"] else self.y + 64

    def Draw(self, dc):
        dc.DrawBitmap(self.Bitmap, self.x, self.y)
        if self.Dialog:
            dc.DrawBitmap(self.Canvas.R["INDICATOR"][2 if self.Dialog.detached else 1], self.x + 42, self.y + 5)
        if self.Canvas.S["TOGGLE_NAME"]:
            if self.Thread and self.Thread.status:
                dc.nameTexts.append("%s %s" % (self.name, self.Thread.status))
            else:
                dc.nameTexts.append(self.name)
            dc.namePoints.append(self.namePos)
        if self.Canvas.S["TOGGLE_ANCR"]:
            for a in self.Anchors:
                a.Draw(dc)

    def LogErr(self, err):
        wx.CallAfter(self.Canvas.F.Record.LogErr, "%s: %s" % (self.__class__.__name__, err))

    def LogOut(self, out):
        wx.CallAfter(self.Canvas.F.Record.LogOut, "%s: %s" % (self.__class__.__name__, out))

    # -------------------------------------------------------- #
    def GetLinkedWidget(self, key=None):
        if key is None:
            for a in self.Anchors:
                for dest in a.connected:
                    yield dest.Widget
        else:
            for dest in self.Key2Anchor[key]:
                yield dest.Widget

    def GetOutgoingWidget(self):
        for a in self.Outgoing:
            for dest in a.connected:
                yield dest.Widget
        if self.UNIQUE:
            for w in self.__RECEIVER__:
                yield w

    def GetIncomingWidget(self):
        for a in self.Incoming:
            for dest in a.connected:
                yield dest.Widget
        for cls, key in self.PROVIDER:
            yield cls.__INSTANCE__

    def IsOutgoingAvailable(self):
        for a in self.Outgoing:
            if not a.connected:
                return False
        return True

    def IsIncomingAvailable(self):
        for a in self.Incoming:
            if not a.connected:
                return False
        for cls, key in self.PROVIDER:
            if cls.__INSTANCE__ is None:
                return False
        return True

    def IsInternalAvailable(self):
        for field in self.INTERNAL:
            if self.Data[field.key if isinstance(field, BaseField) else field] is None:
                return False
        return True

    # -------------------------------------------------------- #
    def UpdateData(self):
        self.UpdateIncoming()
        self.UpdateOutgoing()
        self.UpdateDialog()

    def UpdateIncoming(self):
        for a in self.Incoming:
            self[a.key] = a.Retrieve()
        for cls, key in self.PROVIDER:
            self[key] = cls.__INSTANCE__ and cls.__INSTANCE__["OUT"]

    def UpdateOutgoing(self):
        self["OUT"] = None

    def UpdateDialog(self):
        if self.Dialog:
            wx.CallAfter(self._UpdateDialog)

    def _UpdateDialog(self):
        if self.Dialog:
            if not self.Dialog.detached:
                self.Dialog.Head.Play("ENTER_THEN_LEAVE")
            self.Dialog.GetData()

    def OnActivation(self):
        if self.Dialog:
            if self.Dialog.detached:
                if self.Dialog.Frame.minimized:
                    self.Dialog.Frame.OnMinimize()
            else:
                if not self.Canvas.F.Harbor.IsShown():
                    self.Canvas.F.HiderR.Click()
                self.Dialog.Head.Play("ENTER_THEN_LEAVE")
            self.Dialog.SetFocus()
        elif self.DIALOG:
            self.Dialog = MakeWidgetDialog(self)
            self.OnShowDialog()

    def StopThread(self):
        if self.THREAD and self.Thread:
            self.Thread.stop = True
            self.Thread = None

    def SaveData(self):
        data = {"OUT": self.Data["OUT"]}
        for key in self.INTERNAL:
            if isinstance(key, BaseField):
                key = key.key
            data[key] = self.Data[key]
        return self.Save(data)

    def LoadData(self, f):
        self.Data.update(self.Load(f))

    # -------------------------------------------------------- #
    def OnBegin(self):
        raise NotImplementedError

    def OnAbort(self):
        raise NotImplementedError

    def OnPause(self):
        raise NotImplementedError

    def OnAlter(self):
        raise NotImplementedError

    def OnShowDialog(self):
        raise NotImplementedError

    def SaveState(self):
        raise NotImplementedError

    def LoadState(self, state):
        raise NotImplementedError

    def Save(self, data):
        return json.dumps(data)

    def Load(self, f):
        return json.load(io.TextIOWrapper(f, "utf-8"))

    def Name(self):
        pass

    def Init(self):
        pass

    def Exit(self):
        pass


# ======================================================= Widget =======================================================
class Widget(BaseWidget):
    __STATES__ = "Idle", "Fail", "Done", "Wait", "Work"

    @Synced
    def OnBegin(self):
        self.OnAlter()
        if not (self.IsIncomingAvailable() and self.IsInternalAvailable()):
            return self.SetState("Fail")
        fail = False
        wait = False
        for w in self.GetIncomingWidget():
            if w.IsState("Idle"):
                w.OnBegin()
            if w.IsState("Fail"):
                fail = True
            elif w.IsState("Work", "Wait"):
                wait = True
        if fail:
            self.SetState("Fail")
        elif wait:
            self.SetState("Wait")
        else:
            self.SetState("Work")

    @Synced
    def OnAbort(self):
        self.OnAlter()

    @Synced
    def OnPause(self):
        pass

    @Synced
    def OnAlter(self):
        if not self.IsState("Idle"):
            self.SetState("Idle")
        self.StopThread()
        self.UpdateData()
        for w in self.GetOutgoingWidget():
            w.OnAlter()

    def OnShowDialog(self):
        if self.THREAD:
            if self.IsState("Work", "Wait"):
                self.Dialog[3].Hide()
                self.Dialog[4].Show()
            else:
                self.Dialog[4].Hide()
                self.Dialog[3].Show()
            self.Dialog.Layout()

    def DialogRun(self):
        if self.THREAD and self.Dialog:
            self.Dialog[3].Hide()
            self.Dialog[4].Show()
            self.Dialog.Layout()

    def DialogStop(self):
        if self.THREAD and self.Dialog:
            self.Dialog[4].Hide()
            self.Dialog[3].Show()
            self.Dialog.Layout()

    def SaveState(self):
        if self.state in ("Work", "Wait"):
            return "Idle"
        return self.state

    def LoadState(self, state):
        self.OnLeave(self.state)
        self.state = state
        self.OnEnter(self.state)

    # -------------------------------------------------------- #
    def Run(self):
        if self.THREAD:
            self.Thread = Thread(target=self.RunInThread)
            self.Thread.start()
        else:
            self.RunDirectly()

    def GetThread(self):
        return threading.currentThread()

    def IsCurrentThread(self):
        return self.Thread == threading.currentThread()

    def Checkpoint(self, *args):
        threading.currentThread().Checkpoint(*args)

    def RunInThread(self):
        try:
            out = self.Task()
            with self.Canvas.Lock:
                if self.IsState("Work") and self.IsCurrentThread():
                    self["OUT"] = out
                    if out is None:
                        self.SetState("Fail")
                        self.LogErr(self.Canvas.L["WIDGET_FAIL"])
                    else:
                        self.SetState("Done")
                        self.LogOut(self.Canvas.L["WIDGET_DONE"])
                    self.Thread = None
        except Interrupted:
            pass
        except Exception as e:
            with self.Canvas.Lock:
                if self.IsState("Work") and self.IsCurrentThread():
                    self.SetState("Fail")
                    self.LogErr(str(e))
                    self.Thread = None

    def RunDirectly(self):
        try:
            self["OUT"] = self.Task()
            if self["OUT"] is None:
                self.SetState("Fail")
                self.LogErr(self.Canvas.L["WIDGET_FAIL"])
            else:
                self.SetState("Done")
                self.LogOut(self.Canvas.L["WIDGET_DONE"])
        except Exception as e:
            self.SetState("Fail")
            self.LogErr(str(e))

    # -------------------------------------------------------- #
    def OnLeaveIdle(self):
        pass

    def OnEnterIdle(self):
        self.Bitmap = self.__RES__["CANVAS"]["IDLE"]

    def OnLeaveWait(self):
        wx.CallAfter(self.DialogStop)

    def OnEnterWait(self):
        self.Bitmap = self.__RES__["CANVAS"]["WAIT"]
        wx.CallAfter(self.DialogRun)

    def OnLeaveWork(self):
        self.Canvas.WidgetRunning(False)
        wx.CallAfter(self.DialogStop)

    def OnEnterWork(self):
        self.Bitmap = self.__RES__["CANVAS"]["WORK"]
        self.Canvas.WidgetRunning(True)
        wx.CallAfter(self.DialogRun)
        self.Run()

    def OnLeaveFail(self):
        self.Reset()

    def OnEnterFail(self):
        self.Bitmap = self.__RES__["CANVAS"]["FAIL"]
        self.UpdateDialog()
        for w in self.GetOutgoingWidget():
            if w.IsState("Wait"):
                w.SetState("Fail")

    def OnLeaveDone(self):
        self.Reset()

    def OnEnterDone(self):
        self.Bitmap = self.__RES__["CANVAS"]["DONE"]
        self.UpdateDialog()
        for w in self.GetOutgoingWidget():
            if w.IsState("Idle"):
                w.UpdateIncoming()
            elif w.IsState("Fail"):
                w.UpdateIncoming()
            elif w.IsState("Wait"):
                w.UpdateIncoming()
                for v in w.GetIncomingWidget():
                    if not v.IsState("Done"):
                        break
                else:
                    w.SetState("Work")

    # -------------------------------------------------------- #
    def Task(self):
        raise Exception(self.Canvas.L["WIDGET_NOT_DEFINED"])

    def Reset(self):
        pass
