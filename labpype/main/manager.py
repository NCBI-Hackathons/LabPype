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
        try:
            if not (UI.FindOrCreateDirectory(self.path)
                    and UI.FindOrCreateDirectory(self.pathInstalled)
                    and UI.FindOrCreateDirectory(self.pathDownloaded)
                    and UI.FindOrCreateDirectory(self.pathTemporary)):
                raise Exception
            self.Manage = None
            self.Gadget = None
            self.Packages = {}  # {"pkgName": pkg, ...}
            self.Widgets = {}  # {"pkgName/widgetClassName": pkg.widgetClass, ...}
            self.Groups = []  # ["groupName", widget, widget, "groupName", ...]
            self.Internal = {"Built-in": builtin}
            self.filename = None
            self.ok = True
        except Exception:
            self.ok = False

    def SetRSL(self, r, s, l):
        self.R = r
        self.S = s
        self.L = l

    def Init(self):
        for name in self.Internal:
            self.AddPackage(name, self.Internal[name])
        if self.pathInstalled not in sys.path:
            sys.path.insert(0, self.pathInstalled)
        failed = []
        for pkgName in os.listdir(self.pathInstalled):
            if os.path.isdir(os.path.join(self.pathInstalled, pkgName)):
                if not self.AddPackage(pkgName):
                    failed.append(pkgName)
        sys.path.remove(self.pathInstalled)
        self.Load(os.path.join(self.path, "widgets.json"))
        return failed

    def GetPackages(self):
        return sorted([i for i in self.Packages if i not in self.Internal])

    # -------------------------------------------------------- #
    def Load(self, filename):
        try:
            if not os.path.exists(filename):
                with open(filename, "wb") as f:
                    f.write(b"[]")
                self.Groups = sum([self.Packages[pkgName].__RAW_GROUP__ for pkgName in self.Internal], [])
            else:
                self.Groups = []
            with open(filename, "r", encoding="utf-8") as f:
                for key, value in json.load(f):
                    if value == "W" and key in self.Widgets:
                        self.Groups.append(self.Widgets[key])
                    elif value == "G":
                        self.Groups.append(key)
            self.filename = filename
            return True
        except Exception:
            return False

    def Save(self):
        try:
            if self.filename is not None:
                out = []
                for i in self.Groups:
                    if isinstance(i, str):
                        out.append((i, "G"))
                    else:
                        out.append((i.__ID__, "W"))
                with open(self.filename, "w", encoding="utf-8") as f:
                    json.dump(out, f)
            return True
        except Exception:
            return False

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
        if not hasattr(pkg, "WIDGETS"):
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
                        icon = os.path.join(os.path.join(self.pathInstalled, pkgName), icon)
                    else:
                        color, widget = row
                        icon = None
                    widget.__COLOR__ = color
                    widget.__ICON__ = icon
                    widget.__ID__ = "%s/%s" % (pkgName, widget.__name__)
                    widget.NAME = self.L.Get(widget.NAME, "WIDGET_NAME_")
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
        self.Gadget.DelItems(pkg.__RAW_GROUP__)
        self.Manage.DelItems(pkg.__RAW_GROUP__)
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
        shutil.rmtree(os.path.join(self.pathInstalled, pkgName))

    # -------------------------------------------------------- #
    def Install(self, fp):
        pathTmp = UI.CreateRandomDirectory(self.pathTemporary)
        exist = []
        done = []
        fail = []
        try:
            with zipfile.ZipFile(fp) as z:
                z.extractall(pathTmp)
        except Exception:
            shutil.rmtree(pathTmp)
            return self.L["GENERAL_HEAD_FAIL"], self.L["MSG_PKG_EXTRACT_FAIL"] % fp
        if self.pathInstalled not in sys.path:
            sys.path.insert(0, self.pathInstalled)
        self.DoInstall(pathTmp, done, exist, fail)
        sys.path.remove(self.pathInstalled)
        shutil.rmtree(pathTmp)
        message = ""
        if done:
            message += "%s\n    %s\n" % (self.L["MSG_PKG_INSTALL_DONE"], ", ".join(done))
        if exist:
            message += "%s\n    %s\n" % (self.L["MSG_PKG_ALREADY_HERE"], ", ".join(exist))
        if fail:
            message += "%s\n    %s\n" % (self.L["MSG_PKG_INSTALL_FAIL"], ", ".join(fail))
        return self.L["MSG_PKG_INSTALL_HEAD"], message[:-1]

    def DoInstall(self, path, done, exist, fail):
        for pkgName in os.listdir(path):
            fullPath = os.path.join(path, pkgName)
            if not os.path.isdir(fullPath):
                continue
            if os.path.exists(os.path.join(fullPath, "__init__.py")):
                if os.path.exists(os.path.join(self.pathInstalled, pkgName)):
                    exist.append(pkgName)
                else:
                    shutil.move(fullPath, self.pathInstalled)
                    if self.AddPackage(pkgName):
                        done.append(pkgName)
                        self.Gadget.AddItems(self.Packages[pkgName].__RAW_GROUP__)
                        self.Manage.AddItems(self.Packages[pkgName].__RAW_GROUP__)
                    else:
                        fail.append(pkgName)
                        shutil.rmtree(os.path.join(self.pathInstalled, pkgName))
            else:
                self.DoInstall(fullPath, done, exist, fail)
