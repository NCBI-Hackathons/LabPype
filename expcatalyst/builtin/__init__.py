# -*- coding: utf-8 -*-

from ..utility import Here

from .anchor import *
from .flowcontrol import *
from .number import *
from .text import *
# from .ssh import *

Number = [
    "Number",
    ("#55aaff", Number, Here("icon", "Number.png")),
    ("#55aaff", RandomInt, Here("icon", "RandomNumber.png")),
]

Text = [
    "Text",
    ("#ffaa55", Line,),
    ("#ffaa55", Text,),
]

FlowControl = [
    "Flow Control",
    ("#ffffff", Passer, Here("icon", "Passer.png")),
    ("#ffffff", Condition, Here("icon", "Condition.png")),
    ("#ffffff", Wait,),
]

# SSH = [
#     "SSH",
#     ("#99e5cf", SSHClient,),
#     ("#99e5cf", SSHShell,),
# ]
