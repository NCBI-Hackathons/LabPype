# -*- coding: utf-8 -*-

from DynaUI import Setting

__all__ = ["Setting"]

Setting.DEFAULT = {
    # Need to be updated before saving
    "LAST_POS"          : (-1, -1),
    "LAST_SIZE"         : (1280, 800),
    "MAXIMIZED"         : 0,
    "SHOW_GADGET"       : 1,
    "SHOW_HARBOR"       : 1,
    "WIDTH_GADGET"      : 240,
    "WIDTH_HARBOR"      : 240,
    "HEIGHT_RECORD"     : 100,

    # Changed in real-time
    "HISTORY_SCHEME"    : [],
    "HISTORY_PROJECT"   : [],
    "TOGGLE_NAME"       : 1,
    "TOGGLE_ANCR"       : 1,
    "TOGGLE_SNAP"       : 0,
    "TOGGLE_CURV"       : 1,
    "TOGGLE_GADGET_GROUP": 1,
    "TOGGLE_GADGET_LABEL": 1,

    "LANGUAGE"          : "en",

}
