# -*- coding: utf-8 -*-

from ..utility import Here

from .anchor import *
from .flowcontrol import *
from .number import *
from .text import *

Number = [
    "Number",
    ("#55aaff", Number, Here("icon", "Number.png")),
    ("#55aaff", RandomInt, Here("icon", "RandomNumber.png")),
]

Text = [
    "Text",
    ("#ffaa55", Line, ),
    ("#ffaa55", Text, ),
]

FlowControl = [
    "Flow Control",
    ("#d0d0d0", Passer, Here("icon", "Passer.png")),
    ("#d0d0d0", Condition, Here("icon", "Condition.png")),
]
