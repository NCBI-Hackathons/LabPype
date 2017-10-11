# -*- coding: utf-8 -*-


import wx
import DynaUI as UI
from wx.lib.embeddedimage import PyEmbeddedImage
from .utility import PineappleHere

__all__ = ["Resource"]


class Resource(UI.Resource):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Color
        for key, default in {
            "FONTFACE_CANVAS"  : "Microsoft YaHei UI",
            "FONTFACE_MAIN"    : "Simsun",
            "COLOR_CONNECTION" : "#bbbbbb",
            "COLOR_SELECTION"  : "#00c0ff",
            "COLOR_WIDGET_DONE": "#00ff00",
            "COLOR_WIDGET_WAIT": "#ffff00",
            "COLOR_WIDGET_FAIL": "#ff0000",
            "COLOR_ANCHOR_RECV": "#ffffff",
            "COLOR_ANCHOR_SEND": "#c0ffc0",
            "COLOR_ANCHOR_PASS": "#00ff00",
            "COLOR_ANCHOR_FAIL": "#ff0000",
        }.items():
            self[key] = kwargs.get(key, default)
        # GUI
        self["PEN_CONNECTION"] = wx.Pen(self["COLOR_CONNECTION"], 3)
        self["PEN_CONNECTION_SELECTION1"] = wx.Pen(self["COLOR_SELECTION"], 11)
        self["PEN_CONNECTION_SELECTION2"] = wx.Pen(UI.AlphaBlend(self["COLOR_BG_B"], self["COLOR_SELECTION"], 0.5), 9)
        self["PEN_SELECTION"] = wx.Pen(self["COLOR_SELECTION"], 1)
        self["BRUSH_SELECTION"] = wx.Brush(UI.AlphaBlend(self["COLOR_BG_B"], self["COLOR_SELECTION"], 0.3))
        # Brush
        self["BRUSH_WIDGET_DONE"] = wx.Brush(self["COLOR_WIDGET_DONE"])
        self["BRUSH_WIDGET_WAIT"] = wx.Brush(self["COLOR_WIDGET_WAIT"])
        self["BRUSH_WIDGET_FAIL"] = wx.Brush(self["COLOR_WIDGET_FAIL"])
        self["BRUSH_ANCHOR_RECV"] = wx.Brush(self["COLOR_ANCHOR_RECV"])
        self["BRUSH_ANCHOR_SEND"] = wx.Brush(self["COLOR_ANCHOR_SEND"])
        self["BRUSH_ANCHOR_PASS"] = wx.Brush(self["COLOR_ANCHOR_PASS"])
        self["BRUSH_ANCHOR_FAIL"] = wx.Brush(self["COLOR_ANCHOR_FAIL"])
        # Font
        self.SetMainFont(9, self["FONTFACE_MAIN"])
        self["FONT_CANVAS"] = wx.Font(9, 70, 90, wx.FONTWEIGHT_BOLD, False, self["FONTFACE_CANVAS"])
        # IMG_ICON
        self["ICON"] = IMG_ICON.GetIcon()
        # Bitmap
        for key in ("TOOL_OPTION",
                    "TOOL_FILE_N",
                    "TOOL_FILE_O",
                    "TOOL_FILE_S",
                    "TOOL_ALGN_L",
                    "TOOL_ALGN_V",
                    "TOOL_ALGN_R",
                    "TOOL_ALGN_T",
                    "TOOL_ALGN_H",
                    "TOOL_ALGN_B",
                    "TOOL_DIST_H",
                    "TOOL_DIST_V",
                    "TOOL_MOVE_U",
                    "TOOL_MOVE_D",
                    "TOOL_MOVE_T",
                    "TOOL_MOVE_B",
                    "TOOL_T_ANCR",
                    "TOOL_T_NAME",
                    "TOOL_T_SNAP",
                    "TOOL_T_CURV",
                    "TOOL_T_DIAG",
                    "TOOL_T_FSCN",
                    "TOOL_CANCEL",
                    "TOOL_DELETE",
                    "TOOL_T_SHOW",
                    "TOOL_T_TEXT",
                    "TOOL_MANAGE",

                    "DIALOG_MISC",
                    "DIALOG_ATCH",
                    "DIALOG_DTCH",
                    "DIALOG_LOCA",
                    ):
            self[key] = UI.GetBitmaps(self.GetBitmap(key), 20, 20)
        for key in ("MANAGE_ADD",
                    "MANAGE_DEL"
                    ):
            self[key] = self.GetBitmap(key)
        # Resources of widget
        self["WIDGET_CANVAS"] = {}
        self["WIDGET_CANVAS_DONE"] = {}
        self["WIDGET_CANVAS_FAIL"] = {}
        self["WIDGET_CANVAS_WAIT"] = {}
        self["WIDGET_BUTTON"] = {}
        self["WIDGET_CURSOR"] = {}
        # Resources for widget
        self.DefaultIcon = IMG_WIDGET.GetBitmap()
        self.MaskCanvas = IMG_MASK_CANVAS.GetBitmap()
        self.MaskGadget = IMG_MASK_GADGET.GetBitmap()
        self.MaskCursor = IMG_MASK_CURSOR.GetBitmap()
        self.RectCanvas = wx.Rect(0, 0, 56, 56)
        self.RectGadget = wx.Rect(0, 0, 32, 32)
        self.RectCursor = wx.Rect(0, 0, 30, 30)
        self.WidgetPen = wx.Pen("#000000", 1)
        self.WidgetBrush = wx.Brush("#00000060")

    def GetBitmap(self, key):
        return wx.Bitmap(PineappleHere("image", key + ".png"))

    def DrawWidgets(self, widgetList):
        mdc = wx.MemoryDC()
        for widget in widgetList:
            if isinstance(widget, tuple):
                self._DrawWidget(mdc, *widget)
        mdc.SelectObject(wx.NullBitmap)

    def DrawWidget(self, widget):
        mdc = wx.MemoryDC()
        self._DrawWidget(mdc, *widget)
        mdc.SelectObject(wx.NullBitmap)

    def _PrepareWidgetIcon(self, path=""):
        bitmap = wx.Bitmap(path) if path else self.DefaultIcon
        w, h = bitmap.GetSize()
        if w > 30 or h > 30:
            r = max(w, h) / 30
            w /= r
            h /= r
            img = bitmap.ConvertToImage()
            img.Rescale(w, h, wx.IMAGE_QUALITY_HIGH)
            bitmap = img.ConvertToBitmap()
        return bitmap, w // 2, h // 2

    def _DrawWidget(self, mdc, color, cls, path=""):
        key = id(cls)
        if key in self["WIDGET_CANVAS"]:
            return
        cls.KEY = key
        brush = wx.Brush(color)
        bitmap, w2, h2 = self._PrepareWidgetIcon(path)
        self.WidgetPen.SetColour(UI.AlphaBlend("#ffffff", color, 0.75))
        self["WIDGET_CANVAS"][key] = self.MaskCanvas.GetSubBitmap(self.RectCanvas)  # large icon for canvas
        self["WIDGET_BUTTON"][key] = self.MaskGadget.GetSubBitmap(self.RectGadget)  # small icon for gadget/manage panel
        self["WIDGET_CURSOR"][key] = self.MaskCursor.GetSubBitmap(self.RectCursor)  # cursor for drag and add widget
        # For Canvas
        mdc.SelectObject(self["WIDGET_CANVAS"][key])
        mgc = wx.GraphicsContext.Create(mdc)
        mgc.SetPen(self.WidgetPen)
        mgc.SetBrush(brush)
        mgc.DrawRectangle(4, 4, 48, 48)
        mgc.SetBrush(self.WidgetBrush)
        mgc.DrawRectangle(5, 5, 8, 8)
        mdc.DrawBitmap(bitmap, 28 - w2, 28 - h2)
        mdc.SelectObject(wx.NullBitmap)
        for suffix in ("DONE", "FAIL", "WAIT"):
            self["WIDGET_CANVAS_" + suffix][key] = self["WIDGET_CANVAS"][key].GetSubBitmap(self.RectCanvas)
            mdc.SelectObject(self["WIDGET_CANVAS_" + suffix][key])
            mgc = wx.GraphicsContext.Create(mdc)
            mgc.SetBrush(self["BRUSH_WIDGET_" + suffix])
            mgc.DrawRectangle(7, 7, 6, 6)
        # For Gadget
        mdc.SelectObject(self["WIDGET_BUTTON"][key])
        mgc = wx.GraphicsContext.Create(mdc)
        mgc.SetPen(self.WidgetPen)
        mgc.SetBrush(brush)
        mgc.DrawRectangle(0, 0, 30, 30)
        mdc.DrawBitmap(bitmap, 15 - w2, 15 - h2)
        # For Cursor
        mdc.SelectObject(self["WIDGET_CURSOR"][key])
        mgc = wx.GraphicsContext.Create(mdc)
        mgc.SetPen(self.WidgetPen)
        mgc.SetBrush(wx.Brush(color + "60"))
        mdc.DrawBitmap(bitmap, 15 - w2, 15 - h2)
        mgc.DrawRectangle(0, 0, 29, 29)
        self["WIDGET_CURSOR"][key] = wx.Cursor(self["WIDGET_CURSOR"][key].ConvertToImage())


# ----------------------------------------------------------------------
IMG_MASK_CANVAS = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAADgAAAA4CAYAAACohjseAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAMdJREFUeNrs2+0JgCAQgOEumqIFBKeoyZvDBRpDQ0iIyOpHUHe9ByH4'
    b'ywc/41RSSo3laBvjAVB7dPsK732fyzI3Y4yvN1JEDutr60cIYT7tQe0Lj3NuqgILLpdfgZa27L8L5HA5By1sIa1V2K0hyjYBECBAgAD/dti29gPMEAUIECBAgAABAgQIECDAe8Cc6KglO+hBgAABAgQI'
    b'ECDATwG1H91IvmhPxjAHAQIECPDRbSJfJt3etzQHXJFjuW+pPcT6s4JFgAEAKZVQWxhQCe4AAAAASUVORK5CYII=')

# ----------------------------------------------------------------------
IMG_MASK_CURSOR = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAC5JREFUeNrszTEBADAIAzCYcpwXCTt5EgPpJFMHXh0Ri8VisVgsFovF'
    b'YvHfCjAAKQsDuX2dHo0AAAAASUVORK5CYII=')

# ----------------------------------------------------------------------
IMG_MASK_GADGET = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAFdJREFUeNrs17ERwCAMQ1HEsUGGyWRsxWys4NhFVkAFX4Vd+p06KyKa'
    b'M915XNIrZwMJWNYGMo8b0AAAAAAAAAAAAAAAAADgesAe/5eaa9avdvJ4jU+AAQCq0QnVXS7m/gAAAABJRU5ErkJggg==')

# ----------------------------------------------------------------------
IMG_ICON = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAIGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAALOSURBVHjaxJdLbhNB'
    b'EIa/sp2HiK1ABBIrJJASBUUsWLBh5T4AG87iHWt2PgtXGPbcIIqECIg8lIREk5cdj4tFqq2awRNmEjlpyWqru6b+6urqb3pEVXnI1qr7gIgIIEATaNh/BcZABqjWWJXUyYCJN7lWGbnxR8AicAkMgaxq'
    b'EHUzIFE8hDARUFURkXmgDZxaIJUCaNQMoOnF1/p9AEIIqqrHwGPLRLOqw7oBTOyjeOytLQMLdfw2brMFAJu9Xq63NucKcyZFuGDbcO5rIEkSEZF1y8A2cKSqg0pOVbXyz1a4AqyoKt1uNxb7BvDB+hVg'
    b'rqrPuluQWYW3C+OvgD0gtflsVjWgwJWJ+Hbsjt9V1SOY40AVwrnn0oKfLeDJbYjZmkK4qwLhltzKYt1cxCI0BoiIjM32PF9ipf6GIpK1KhBuEXhqD6Ve/Gs/odsLPojnwDPgrGhbRszGNMIlrTVPuCNV'
    b'3VbV/aK47812V1W/F22TflpKTFFVRGRBVQchBI3iAGG0ObVwoqhv3V6YahvFAUKvE5nxDvgFHMUAFlX10mcgiidJkqNaMQNevMw26aeEXsdD6z3wAzicZOAGwm3YOT8GtlR1p1gDzvYN8BL4U7R1Nqu2'
    b'BbkMzAEdYGx7FKt2HVg1yJza8KGq7k1x/NZsfwInNnWgqvvO3yrwwmwOgDQG0LCiaFt0y4bdzIRTB58l4EJVd0MI6lb+2la1Y6cA89kxv007yiceXC1HuKENjkywYdAYFDhwYUfNtzXgN7BrK7t0b8dT'
    b'94r2/obANYjsEGdO6KyEhGLze4UAvllQA5uP9tlN/iYkjEE4g5vuhCN/YhyEhv4yUsXfna9kyZdPOQjZXt/PlSyKx95a+96uZOHj51wfM/SQV7IcYKpeyep+F4yBJRGZV1UpAczgf4V3lwyUAesfwKjq'
    b'eBYZqAKsYZ0rmdT9On7Qj9NZtL8DACozSphP5UC3AAAAAElFTkSuQmCC')

# ----------------------------------------------------------------------
IMG_WIDGET = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAn5JREFUeNrEV02LE0EQna+YoFlcRcGToLCiLB48ePGU3BU8+DM9ePCe'
    b'H+BfWBBXcRNZdZdkN5tJJvG98DpUmsykRwIpKKZnuva9ru6ql954sVhEoRbD+ICn8ERjAszhBceLQMA4lFikJCT6zHy/jUcLfgPPuYAQ8iwKt9iRdrvdFTDeuaZbGLbhIy1gK3FSgzi1pG/ff1h+5Dvs'
    b'AsNDZZ6GgNUhXsU6UveU3YU3QzGTultN+/zp49pT1jAFt9Piamq7r+0Z93o9nvFzZXwK/4OYyVZAEoe4MrpP53un03HFewx/pyfnGyF4dba6UMW2ve9P4QP4UPPFrs+Y6U0Fbu3CtNE0pJVWfRyiSOZv'
    b'hh7GCfxeXYXLPEWaeop0x2TiamLsiks9TIi5Yq/Xy6cUL8+2KBIF4YGCh5aUPcx2MuSP8Pkh/MqP3aRwyRZFYmucwn/5pBti+/CvZbG+wjHbJvuOE1aJPHGIfNWyFhLLGPX8a7z+IHELxDf+FjpxsEB+'
    b'Fpa0KtbGwN5g+C2WvpYp0rH6lFt0gpizCsCXGD6B//VjTcyRtnqZMRXpgKWuM3BVSBk8kjiM9Pk3YgYbAF8p9jv8UlPnPG+Dx/nHijmP1WctVduhNLehfhsZRYrUDmMWEslNpi+YBfxMVR0J80C4qVry'
    b'0glOpsbORTITUaJmn3h9PFbLWHsG/wnvMxOzyIYwmxvw8kxNWBiCqxLlijU/8Ii/aDETzbv4ogovcxJjJqruXDPbAUY8cnsJCMHb1dWnr7Pcy9Wnva+rT7qPq89KGEKvPnXu1cufPv7CsKBKhGFSVVD/'
    b'm3GZ0KwJA9sSmPNdZhwiNHno1Sfe1z9t/wQYAM2LHjPomwPyAAAAAElFTkSuQmCC')
