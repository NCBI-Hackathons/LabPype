# -*- coding: utf-8 -*-

from ..utility import Find
from .anchor import *
from .flowcontrol import *
from .operation import *

__all__ = [
    "ANCHORS",
    "WIDGETS",
    "AnchorFCFS",
]

ANCHORS = []

WIDGETS = [
    "Flow Control",
    ("#ffffff", Passer, Find("builtin/icon", "Passer.png")),
    ("#ffffff", Condition, Find("builtin/icon", "Condition.png")),
    ("#ffffff", Wait,),
    # "General Operation",
    # ("#c0ffff", Merge,),
    # ("#c0ffff", Filter,),
]
