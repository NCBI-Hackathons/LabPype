# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import zipfile
import importlib
import DynaUI as UI
from ..widget import LegitLink, LinkageRedefinedError
from .. import builtin

__all__ = ["Manager"]


class RedefinedError(Exception):
    """Raise to Stop the installation of a package"""


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
            self.R = None
            self.L = None
            self.Manage = None
            self.Gadget = None
            self.Packages = {}  # {"pkgName": pkg, ...}
            self.Widgets = {}  # {"pkgName.widgetClassName": pkg.widgetClass, ...}
            self.Groups = []  # ["groupName", widget, widget, "groupName", ...]
            self.ok = True
        except Exception:
            self.ok = False
        self.Internal = {"Built-in": builtin}

    def Load(self, filename):
        if not os.path.exists(filename):
            with open(filename, "wb") as f:
                f.write(b"[]")
        self.Groups = []
        with open(filename, "r", encoding="utf-8") as f:
            for key, value in json.load(f):
                if value == "W" and key in self.Widgets:
                    self.Groups.append(self.Widgets[key])
                elif value == "G":
                    self.Groups.append(key)
        self.filename = filename

    def Save(self):
        out = []
        for i in self.Groups:
            if isinstance(i, str):
                out.append((i, "G"))
            else:
                out.append((i.__ID__, "W"))
        if self.filename is not None:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(out, f)

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

    def AddPackage(self, pkgName, pkg=None):
        try:
            if pkg is None:
                pkg = importlib.import_module(pkgName)
            if not self.LoadLinkage(pkg):
                raise Exception
            if not self.LoadFromFunction(pkg, "RESOURCE"):
                raise Exception
            if not self.LoadFromFunction(pkg, "SETTING"):
                raise Exception
            if not self.LoadFromFunction(pkg, "LOCALE"):
                raise Exception
            pkg.__WIDGETS__ = []  # [widget, ...]
            pkg.__GROUPS__ = []  # ["pkgName/groupName", ...]
            pkg.__ORI_GROUP__ = []  # ["pkgName/groupName", widget, widget, "pkgName/groupName", ...]
            for row in pkg.WIDGETS:
                if isinstance(row, str):
                    group = self.L.Get("%s/%s" % (pkgName, row), "WIDGET_GROUP_")
                    pkg.__ORI_GROUP__.append(group)
                    pkg.__GROUPS__.append(group)
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
                    pkg.__ORI_GROUP__.append(widget)
                    pkg.__WIDGETS__.append(widget)
        except Exception:
            return False
        else:
            self.R.DrawWidgets(pkg.__WIDGETS__)
            self.Packages[pkgName] = pkg
            self.Widgets.update((widget.__ID__, widget) for widget in pkg.__WIDGETS__)
            self.Groups.extend(pkg.__ORI_GROUP__)
            return True

    def LoadLinkage(self, pkg):
        try:
            LegitLink.AddBatch(pkg.ANCHORS)
            return True
        except LinkageRedefinedError:
            LegitLink.DelBatch(pkg.ANCHORS)
            return False
        except Exception:
            return False

    def LoadFromFunction(self, pkg, funcName):
        if not hasattr(pkg, funcName):
            return True
        try:
            d = getattr(pkg, funcName).item()
            for key, value in d:
                if key in self.R:
                    raise RedefinedError
                else:
                    self.R[key] = value
            return True
        except RedefinedError:
            for key, value in d:
                if key in self.R:
                    del self.R[key]
            return False
        except Exception:
            return False

    def DelPackage(self, pkgName):
        pkg = self.Packages[pkgName]
        self.Gadget.DelItems(pkg.__ORI_GROUP__)
        self.Manage.DelItems(pkg.__ORI_GROUP__)
        del self.Packages[pkgName]
        for widget in pkg.__WIDGETS__:
            del self.Widgets[widget.__ID__]
            if widget in self.Groups:
                self.Groups.remove(widget)
        for group in pkg.__GROUPS__:
            if group in self.Groups:
                self.Groups.remove(group)
        LegitLink.DelBatch(pkg.ANCHORS)
        shutil.rmtree(os.path.join(self.pathInstalled, pkgName))

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
        for pkgName in os.listdir(pathTmp):
            if os.path.exists(os.path.join(self.pathInstalled, pkgName)):
                exist.append(pkgName)
            else:
                shutil.move(os.path.join(pathTmp, pkgName), self.pathInstalled)
                if self.AddPackage(pkgName):
                    done.append(pkgName)
                    self.Gadget.AddItems(self.Packages[pkgName].__ORI_GROUP__)
                    self.Manage.AddItems(self.Packages[pkgName].__ORI_GROUP__)
                else:
                    fail.append(pkgName)
                    shutil.rmtree(os.path.join(self.pathInstalled, pkgName))
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
