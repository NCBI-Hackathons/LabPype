# -*- coding: utf-8 -*-

AUTHOR = "Yadi Zhou"

if __name__ == "__main__":
    import os
    import sys

    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
    if path not in sys.path:
        sys.path.append(path)
    from labpype.app import App

    App().Start()
else:
    from .app import App
