# -*- coding: utf-8 -*-

import os
import labpype

# Create an application
App = labpype.App(path=os.path.dirname(os.path.realpath(__file__)))
# Start the application using the current folder as the application directory
App.Start()
