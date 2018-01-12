# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import zipfile
import importlib
import DynaUI as UI
from ..widget import LegitLink
from .. import builtin

__all__ = ["Manager"]


class Manager(object):
    def __init__(self, path):
        self.path = path
        self.pathInstalled = os.path.join(path, "installed")
        self.pathDownloaded = os.path.join(path, "downloaded")
        self.pathTemporary = os.path.join(path, "temporary")
        self.ok = all((UI.FindOrCreateDirectory(self.path),
                       UI.FindOrCreateDirectory(self.pathInstalled),
                       UI.FindOrCreateDirectory(self.pathDownloaded),
                       UI.FindOrCreateDirectory(self.pathTemporary)))

    def Init(self, frame):
        self.F = frame
        self.R = frame.R
        self.S = frame.S
        self.L = frame.L
        self.Packages = {}  # {"pkgName": pkg, ...}
        self.Widgets = {}  # {"pkgName/widgetClassName": pkg.widgetClass, ...}
        self.Groups = []  # ["groupName", widget, widget, "groupName", ...]
        self.Internal = {"Built-in": builtin}
        self.filename = os.path.join(self.path, "widgets.json")
        for name in self.Internal:
            self.AddPackage(name, self.Internal[name])
        failed = []
        self.AddSysPath()
        for pkgName in os.listdir(self.pathInstalled):
            if os.path.isdir(self.PathInInstalled(pkgName)):
                if not self.AddPackage(pkgName):
                    failed.append(pkgName)
        self.DelSysPath()
        self.Load()
        if failed:
            self.F.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_PKG_INITIAL_FAIL", textData=",".join(failed))
        self.F.Gadget.AddItems(self.Groups)
        for key, value in self._PendingGroup.items():
            self.F.Gadget.DoToggleGroup(key, value)

    # -------------------------------------------------------- #
    def Load(self):
        self._PendingGroup = {}
        try:
            if not os.path.exists(self.filename):
                with open(self.filename, "wb") as f:
                    f.write(b"[]")
                self.Groups = sum([self.Packages[pkgName].__RAW_GROUP__ for pkgName in self.Packages], [])
            else:
                self.Groups = []
            with open(self.filename, "r", encoding="utf-8") as f:
                for key, value in json.load(f):
                    if value == "W":
                        if key in self.Widgets:
                            self.Groups.append(self.Widgets[key])
                    else:
                        self.Groups.append(key)
                        self._PendingGroup[key] = value
        except Exception:
            pass

    def Save(self):
        out = []
        for i in self.Groups:
            if isinstance(i, str):
                out.append((i, self.F.Gadget.Groups[i]["SHOW"]))
            else:
                out.append((i.__ID__, "W"))
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(out, f)
        except Exception:
            pass

    # -------------------------------------------------------- #
    def LoadLinkage(self, pkg):
        try:
            if hasattr(pkg, "ANCHORS"):
                for link in pkg.ANCHORS:
                    LegitLink.Add(link[1], link[2] if len(link) > 2 else link[1], link[0], *link[3:])
            return True
        except Exception:
            return False

    def LoadResource(self, pkg):
        return self.LoadXXX(pkg, "RESOURCE", self.R)

    def LoadSetting(self, pkg):
        return self.LoadXXX(pkg, "SETTING", self.S)

    def LoadLocale(self, pkg):
        return self.LoadXXX(pkg, "LOCALE", self.L)

    def LoadXXX(self, pkg, funcName, D):
        if not hasattr(pkg, funcName):
            return True
        try:
            items = getattr(pkg, funcName)().items()
            __x__ = getattr(pkg, "__%s__" % funcName)
            for key, value in items:
                if key in D:
                    raise Exception
                else:
                    D[key] = value
                    __x__.append(key)
            return True
        except Exception:
            return False

    # -------------------------------------------------------- #
    def UnloadLinkage(self, pkg):
        if hasattr(pkg, "ANCHORS"):
            for link in pkg.ANCHORS:
                LegitLink.Del(link[1], link[2] if len(link) > 2 else link[1], link[0])

    def UnloadResource(self, pkg):
        self.UnloadXXX(pkg, "RESOURCE", self.R)

    def UnloadSetting(self, pkg):
        self.UnloadXXX(pkg, "SETTING", self.S)

    def UnloadLocale(self, pkg):
        self.UnloadXXX(pkg, "LOCALE", self.L)

    def UnloadXXX(self, pkg, funcName, D):
        if hasattr(pkg, funcName):
            __x__ = getattr(pkg, "__%s__" % funcName)
            for key in __x__:
                del D[key]

    # -------------------------------------------------------- #
    def AddPackage(self, pkgName, pkg=None):
        try:
            if pkg is None:
                pkg = importlib.import_module(pkgName)
        except Exception:
            return False
        pkg.__RESOURCE__ = []
        pkg.__SETTING__ = []
        pkg.__LOCALE__ = []
        pkg.__WIDGET__ = []  # [widget, ...]
        pkg.__GROUP__ = []  # ["pkgName/groupName", ...]
        pkg.__RAW_GROUP__ = []  # ["pkgName/groupName", widget, widget, "pkgName/groupName", ...]
        if not hasattr(pkg, "WIDGETS"):
            return False
        if not self.LoadLinkage(pkg):
            self.UnloadLinkage(pkg)
            return False
        if not self.LoadResource(pkg):
            self.UnloadResource(pkg)
            return False
        if not self.LoadSetting(pkg):
            self.UnloadSetting(pkg)
            return False
        if not self.LoadLocale(pkg):
            self.UnloadLocale(pkg)
            return False
        try:
            for row in pkg.WIDGETS:
                if isinstance(row, str):
                    group = self.L.Get("%s/%s" % (pkgName, row), "WIDGET_GROUP_")
                    pkg.__GROUP__.append(group)
                    pkg.__RAW_GROUP__.append(group)
                else:
                    if len(row) == 3:
                        color, widget, icon = row
                        icon = os.path.join(self.PathInInstalled(pkgName), icon)
                    else:
                        color, widget = row
                        icon = None
                    widget.NAME = self.L.Get(widget.NAME, "WIDGET_NAME_")
                    widget.DESC = self.L.Get(widget.DESC, "WIDGET_DESC_")
                    widget.__COLOR__ = color
                    widget.__ICON__ = icon
                    widget.__ID__ = "%s/%s" % (pkgName, widget.__name__)
                    pkg.__WIDGET__.append(widget)
                    pkg.__RAW_GROUP__.append(widget)
        except Exception:
            return False
        self.R.DrawWidgets(pkg.__WIDGET__)
        self.Packages[pkgName] = pkg
        self.Widgets.update((widget.__ID__, widget) for widget in pkg.__WIDGET__)
        self.Groups.extend(pkg.__RAW_GROUP__)
        return True

    def DelPackage(self, pkgName):
        pkg = self.Packages[pkgName]
        inUse = [w.NAME for w in pkg.__WIDGET__ if w.__INSTANCE__]
        if inUse:
            self.F.OnSimpleDialog("MSG_PKG_DELETE_HEAD", "MSG_PKG_IN_USE_FAIL", textData=(pkgName, "\n".join(inUse)))
            return
        self.F.Gadget.DelItems(pkg.__RAW_GROUP__)
        if self.F.Manage:
            self.F.Manage.DelItems(pkg.__RAW_GROUP__)
        del self.Packages[pkgName]
        for widget in pkg.__WIDGET__:
            del self.Widgets[widget.__ID__]
            if widget in self.Groups:
                self.Groups.remove(widget)
        for group in pkg.__GROUP__:
            if group in self.Groups:
                self.Groups.remove(group)
        self.UnloadLinkage(pkg)
        self.UnloadResource(pkg)
        self.UnloadSetting(pkg)
        self.UnloadLocale(pkg)
        shutil.rmtree(self.PathInInstalled(pkgName))

    def GetPackages(self):
        return sorted([i for i in self.Packages if i not in self.Internal])

    # -------------------------------------------------------- #
    def Install(self, fp):
        pathTmp = self.Extract(fp)
        if pathTmp is None:
            return
        done = []
        exist = []
        fail = []
        copy = []
        req = []
        self.AddSysPath()
        self.DoInstall(pathTmp, done, exist, fail, copy, req)
        self.DelSysPath()
        shutil.rmtree(pathTmp)
        self.F.OnSimpleDialog("MSG_PKG_INSTALL_HEAD", "MSG_PKG_INSTALL_INFO",
                              textData=(", ".join(done) or "-", ", ".join(exist) or "-", ", ".join(fail) or "-", ", ".join(copy) or "-", ", ".join(req) or "-"))

    def DoInstall(self, path, done, exist, fail, copy, req, topLevel=True):
        reqFile = os.path.join(path, "requirements.txt")
        if os.path.exists(reqFile):
            copyOnly = True
            with open(reqFile) as f:
                req.extend(f.read().splitlines())
        else:
            copyOnly = False
        for pkgName in os.listdir(path):
            fullPath = os.path.join(path, pkgName)
            if not os.path.isdir(fullPath):
                continue
            if os.path.exists(os.path.join(fullPath, "__init__.py")):
                if os.path.exists(self.PathInInstalled(pkgName)):
                    exist.append(pkgName)
                else:
                    shutil.move(fullPath, self.pathInstalled)
                    if copyOnly:
                        copy.append(pkgName)
                    else:
                        if self.AddPackage(pkgName):
                            done.append(pkgName)
                            self.F.Gadget.AddItems(self.Packages[pkgName].__RAW_GROUP__)
                            if self.F.Manage:
                                self.F.Manage.AddItems(self.Packages[pkgName].__RAW_GROUP__)
                        else:
                            fail.append(pkgName)
                            shutil.rmtree(self.PathInInstalled(pkgName))
            elif topLevel:
                self.DoInstall(fullPath, done, exist, fail, copy, req, False)

    def Extract(self, fp):
        pathTmp = UI.CreateRandomDirectory(self.pathTemporary)
        try:
            with zipfile.ZipFile(fp) as z:
                z.extractall(pathTmp)
            return pathTmp
        except Exception:
            shutil.rmtree(pathTmp)
            self.F.OnSimpleDialog("GENERAL_HEAD_FAIL", "MSG_PKG_EXTRACT_FAIL", textData=fp)

    # -------------------------------------------------------- #
    def AddSysPath(self):
        if self.pathInstalled not in sys.path:
            sys.path.insert(0, self.pathInstalled)

    def DelSysPath(self):
        if self.pathInstalled in sys.path:
            sys.path.remove(self.pathInstalled)

    def PathInInstalled(self, name):
        return os.path.join(self.pathInstalled, name)

    def PathInDownloaded(self, name):
        return os.path.join(self.pathDownloaded, name)

    def PathInTemporary(self, name):
        return os.path.join(self.pathTemporary, name)
