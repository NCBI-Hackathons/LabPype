# -*- coding: utf-8 -*-

import io
import wx
import math
import json
import threading
from DynaUI import GetMultiLineTextExtent, DoNothing
from .dialog import MakeWidgetDialog, Dialog
from .base import Base, IdPool
from .field import BaseField
from .anchor import Anchor

__all__ = [
    "BaseWidget",
    "Widget",
    "Thread",
    "Synced",
]


# ================================================== How to Subclass ===================================================
#   Widget subclasses should have the following class properties:
#       KEY       -  Class Identifier. By default KEY is id(WidgetClass). Normally user does not need to specify KEY.
#       NAME      -  Default name of the widget, for display purpose.
#       DIALOG    -  Associated Dialog class for interacting with the widget. Optional.
#       THREAD    -  Whether the task should be done in a separate thread.
#       INTERNAL  -  KEY for data that are input from the associated dialog.
#       INCOMING  -  Incoming anchor(s): (AnchorType, KEY:str, IsMultiple:bool, Position:int, Name:str(""), AnchorClass:) [, (more anchors...)]
#       OUTGOING  -  AnchorType of the data sending out: AnchorType [, Name:str(""), AnchorClass]
#   The following methods should be re-implemented:
#       Name      -  How canvas display the name of this widget. Default is cls.NAME
#       Task      -  to do
#       Save      -  to do
#       Load      -  to do
#   Destroy must be called when deleting the widget to (i)clear links; (ii)close dialog; (iii)stop thread; (iv)release id
# ======================================================================================================================


# ======================================================== Misc ========================================================
class Interrupted(Exception):
    """Raise to interrupt running thread"""


def Synced(func):
    def SyncedFunc(self, *args, **kwargs):
        if self.THREAD:
            with self.Canvas.Lock:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)

    return SyncedFunc


class Thread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDaemon(True)
        self.stop = False
        self.progress = ()

    def CheckPoint(self, *args):
        if self.stop:
            raise Interrupted
        self.progress = args


# ===================================================== BaseWidget =====================================================
class BaseWidget(Base):
    NAME = ""
    DIALOG = None
    THREAD = False
    INTERNAL = None
    INCOMING = None
    OUTGOING = None
    SINGLETON = False

    __COLOR__ = None
    __ICON__ = None
    __RES__ = None
    __ID__ = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "__INITIALIZED__"):
            cls.__INITIALIZED__ = True
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
            if cls.OUTGOING is None:
                pass
            elif not isinstance(cls.OUTGOING, (tuple, list)):
                cls.OUTGOING = (cls.OUTGOING, "Output", None)
        return super().__new__(cls)

    def __init__(self, canvas, states):
        super().__init__(w=68, h=68)
        self.Canvas = canvas
        self.Record = canvas.GetParent().Record
        self.Bitmap = None
        self.name = None
        self.namePos = None
        self.nameSize = None
        self.Dialog = None
        self.DialogPos = None
        self.DialogSize = None
        self.Thread = None
        self.Data = {}
        self.Incoming = []
        self.Outgoing = []
        self.Key2Anchor = {}
        self.Pos2Anchor = {"L": [], "T": [], "R": [], "B": []}
        if self.INTERNAL:
            for field in self.INTERNAL:
                self.Data[field.key if isinstance(field, BaseField) else field] = None
        if self.INCOMING:
            for args in self.INCOMING:
                self.AddAnchor(False, *args)
        if self.OUTGOING:
            self.AddAnchor(True, self.OUTGOING[0], "OUT", True, "RBT", self.Canvas.L.Get(self.OUTGOING[1], "ANCHOR_NAME_"), self.OUTGOING[2])
        self.Anchors = self.Incoming + self.Outgoing
        if self.__class__.SINGLETON:
            self.__class__.SINGLETON = self
        self.state = None
        self.SetState(states[0])
        self.Init()

    # -------------------------------------------------------- #
    @Synced
    def Destroy(self):
        self.Exit()
        getattr(self, "OnLeave%s" % self.state, DoNothing)()
        if self.Dialog:
            self.Dialog.OnClose()
        self.StopThread()
        for a in reversed(self.Anchors):
            a.EmptyTarget(a.send)
            IdPool.Release(a.Id)
        IdPool.Release(self.Id)
        if isinstance(self.__class__.SINGLETON, self.__class__):
            self.__class__.SINGLETON = True
        self.Data = None

    @Synced
    def IsState(self, state):
        if isinstance(state, tuple):
            return self.state in state
        else:
            return self.state == state

    @Synced
    def SetState(self, state):
        getattr(self, "OnLeave%s" % self.state, DoNothing)()
        self.state = state
        getattr(self, "OnEnter%s" % self.state, DoNothing)()
        self.SetName()
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
        self.Pos2Anchor[a.pos].append(a)

    def SetName(self):
        name = self.Name()
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
            if a.posAuto and a.connected:
                self.Pos2Anchor[a.pos].remove(a)
                x = sum(i.x for i in a.connected) / len(a.connected) - self.x - 25
                y = sum(i.y for i in a.connected) / len(a.connected) - self.y - 25
                theta = math.atan2(y, x) * 4
                if "T" in a.posAllowed and -3.0 * math.pi <= theta < -math.pi:
                    a.pos = "T"
                elif "R" in a.posAllowed and -math.pi <= theta < math.pi:
                    a.pos = "R"
                elif "B" in a.posAllowed and math.pi <= theta < 3 * math.pi:
                    a.pos = "B"
                elif "L" in a.posAllowed and (3 * math.pi <= theta or theta < -3.0 * math.pi):
                    a.pos = "L"
                self.Pos2Anchor[a.pos].append(a)
        for p in "LRTB":
            n = len(self.Pos2Anchor[p])
            for index, a in enumerate(self.Pos2Anchor[p]):
                self._PositionAnchor(a, index * 18 + (1 - n) * 9)

    def _PositionAnchor(self, a, offset=0):
        if a.pos == "L":
            ax = -6
        elif a.pos == "R":
            ax = 56
        else:
            ax = 25 + offset
        if a.pos == "T":
            ay = -6
        elif a.pos == "B":
            ay = 56
        else:
            ay = 25 + offset
        a.SetPosition(self.x + ax, self.y + ay)

    def PositionName(self):
        self.namePos = self.x + 28 - self.nameSize[0] // 2, self.y - self.nameSize[1] - 8 if len(self.Anchors) == 1 and self.Anchors[0].pos == "B" else self.y + 64

    def Draw(self, dc):
        dc.DrawBitmap(self.Bitmap, self.x, self.y)
        if self.Dialog:
            dc.DrawBitmap(self.Canvas.R["DIALOG_DTCH" if self.Dialog.detached else "DIALOG_ATCH"][3], self.x + 36, self.y)
        if self.Canvas.S["TOGGLE_NAME"]:
            if self.Thread and self.Thread.progress:
                dc.nameTexts.append("%s (%s/%s)" % (self.name, self.Thread.progress[0], self.Thread.progress[1]))
            else:
                dc.nameTexts.append(self.name)
            dc.namePoints.append(self.namePos)
        if self.Canvas.S["TOGGLE_ANCR"]:
            for a in self.Anchors:
                a.Draw(dc)

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

    def GetIncomingWidget(self):
        for a in self.Incoming:
            for dest in a.connected:
                yield dest.Widget

    def IsOutgoingAvailable(self):
        for a in self.Outgoing:
            if not a.connected:
                return False
        return True

    def IsIncomingAvailable(self):
        for a in self.Incoming:
            if not a.connected:
                return False
        return True

    def IsInternalAvailable(self):
        for field in self.INTERNAL:
            if self.Data[field.key if isinstance(field, BaseField) else field] is None:
                return False
        return True

    # -------------------------------------------------------- #
    def UpdateData(self):
        for a in self.Incoming:
            if a.connected:
                if a.multiple:
                    self[a.key] = [dest.Widget[dest.key] for dest in a.connected]
                else:
                    self[a.key] = a.connected[0].Widget[a.connected[0].key]
            else:
                self[a.key] = None
        for a in self.Outgoing:
            self[a.key] = None

    def UpdateDialog(self):
        if self.Dialog:
            if not self.Dialog.detached:
                wx.CallAfter(self.Dialog.Head.Play, "ENTER_THEN_LEAVE")
            wx.CallAfter(self.Dialog.GetData)

    def OnActivation(self):
        if self.Dialog:
            if self.Dialog.detached:
                if self.Dialog.Frame.minimized:
                    self.Dialog.Frame.OnMinimize()
            else:
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
        return self.Save()

    def LoadData(self, f):
        self.Data = self.Load(f)
        self.SetName()

    # -------------------------------------------------------- #
    def OnBegin(self):
        raise NotImplementedError

    def OnAlter(self):
        raise NotImplementedError

    def OnShowDialog(self):
        raise NotImplementedError

    def SaveState(self):
        raise NotImplementedError

    def LoadState(self, state):
        raise NotImplementedError

    def Name(self):
        return self.NAME

    def Save(self):
        return json.dumps(self.Data)

    def Load(self, f):
        return json.load(io.TextIOWrapper(f, "utf-8"))

    def Init(self):
        pass

    def Exit(self):
        pass


# ======================================================= Widget =======================================================
class Widget(BaseWidget):
    def __init__(self, canvas):
        super().__init__(canvas, ("Idle", "Fail", "Done", "Wait", "Work"))

    def OnBegin(self):
        if not (self.IsIncomingAvailable() and self.IsInternalAvailable()):
            self.SetState("Fail")
            return
        fail = False
        wait = False
        for w in self.GetIncomingWidget():
            if w.IsState("Idle"):
                w.OnBegin()
            if w.IsState("Fail"):
                fail = True
            elif w.IsState(("Work", "Wait")):
                wait = True
        if fail:
            self.SetState("Fail")
        elif wait:
            self.SetState("Wait")
        else:
            self.SetState("Work")

    def OnAlter(self):
        self.SetState("Idle")
        self.StopThread()
        self.UpdateData()
        for w in self.GetOutgoingWidget():
            w.OnAlter()

    def OnShowDialog(self):
        if self.THREAD and self.Dialog:
            if self.IsState(("Work", "Wait")):
                self.Dialog[3].Hide()
                self.Dialog[4].Show()
            else:
                self.Dialog[4].Hide()
                self.Dialog[3].Show()
            self.Dialog.Layout()

    def SaveState(self):  # TODO
        if self.state in ("Work", "Wait"):
            return "Idle"
        return self.state

    def LoadState(self, state):  # TODO
        try:
            self.SetState(state)
        except Exception as e:
            print(e)

    # -------------------------------------------------------- #
    def Run(self):
        if self.THREAD:
            self.Thread = Thread(target=self.RunInThread)
            self.Thread.start()
        else:
            self.RunDirectly()

    def RunInThread(self):
        try:
            out = self.Task()
            with self.Canvas.Lock:
                if self.IsState("Work") and self.Thread == threading.currentThread():
                    self["OUT"] = out
                    if out is None:
                        self.SetState("Fail")
                        self.Record.LogFail("%s: %s" % (self.__class__.__name__, self.Canvas.L["WIDGET_FAIL"]))
                    else:
                        self.SetState("Done")
                        self.Record.LogDone("%s: %s" % (self.__class__.__name__, self.Canvas.L["WIDGET_DONE"]))
        except Interrupted:
            pass
        except Exception as e:
            with self.Canvas.Lock:
                if self.IsState("Work") and self.Thread == threading.currentThread():
                    self.SetState("Fail")
                    self.Record.LogFail("%s: %s" % (self.__class__.__name__, str(e)))
        finally:
            self.Thread = None

    def RunDirectly(self):
        try:
            self["OUT"] = self.Task()
            if self["OUT"] is None:
                self.SetState("Fail")
                self.Record.LogFail("%s: %s" % (self.__class__.__name__, self.Canvas.L["WIDGET_FAIL"]))
            else:
                self.SetState("Done")
                self.Record.LogDone("%s: %s" % (self.__class__.__name__, self.Canvas.L["WIDGET_DONE"]))
        except Exception as e:
            self.SetState("Fail")
            self.Record.LogFail("%s: %s" % (self.__class__.__name__, str(e)))

    # -------------------------------------------------------- #
    def OnLeaveIdle(self):
        pass

    def OnEnterIdle(self):
        self.Bitmap = self.__RES__["CANVAS"]["IDLE"]
        # self.UpdateData()

    def OnLeaveWait(self):
        if self.THREAD and self.Dialog:
            self.Dialog[4].Hide()
            self.Dialog[3].Show()
            self.Dialog.Layout()

    def OnEnterWait(self):
        self.Bitmap = self.__RES__["CANVAS"]["WAIT"]
        if self.THREAD and self.Dialog:
            self.Dialog[3].Hide()
            self.Dialog[4].Show()
            self.Dialog.Layout()

    def OnLeaveWork(self):
        self.Canvas.WidgetRunning(False)
        if self.THREAD and self.Dialog:
            self.Dialog[4].Hide()
            self.Dialog[3].Show()
            self.Dialog.Layout()

    def OnEnterWork(self):
        self.Bitmap = self.__RES__["CANVAS"]["WORK"]
        self.Canvas.WidgetRunning(True)
        if self.THREAD and self.Dialog:
            self.Dialog[3].Hide()
            self.Dialog[4].Show()
            self.Dialog.Layout()
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
                w.UpdateData()
            elif w.IsState("Fail"):
                w.UpdateData()
            elif w.IsState("Wait"):
                w.UpdateData()
                for v in w.GetIncomingWidget():
                    if not v.IsState("Done"):
                        break
                else:
                    w.SetState("Work")

    # -------------------------------------------------------- #
    def Task(self):
        return False

    def Reset(self):
        pass