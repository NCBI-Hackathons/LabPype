# -*- coding: utf-8 -*-

from DynaUI import Setting

__all__ = ["Setting"]

Setting.DEFAULT = {
    # Need to be updated before saving
    "LAST_POS"       : (-1, -1),
    "LAST_SIZE"      : (1280, 800),
    "MAXIMIZED"      : 0,
    "SHOW_GADGET"    : 1,
    "SHOW_HARBOR"    : 1,
    "SHOW_CENTER"    : 1,
    "WIDTH_GADGET"   : 264,
    "WIDTH_HARBOR"   : 264,
    "HEIGHT_CENTER"  : 100,

    # Changed in real-time
    "HISTORY_SCHEME" : [],
    "HISTORY_PROJECT": [],
    "TOGGLE_NAME"    : 1,
    "TOGGLE_ANCR"    : 1,
    "TOGGLE_SNAP"    : 0,
    "TOGGLE_CURV"    : 1,
    "TOGGLE_G_GROUP" : 1,
    "TOGGLE_G_LABEL" : 1,

    "LANGUAGE"       : "en",

}
