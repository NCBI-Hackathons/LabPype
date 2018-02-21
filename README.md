# LabPype

[![PyPI version](https://badge.fury.io/py/LabPype.svg)](https://badge.fury.io/py/LabPype)
[![Python35](https://img.shields.io/badge/python-3.5-blue.svg)](https://badge.fury.io/py/LabPype)
[![Python36](https://img.shields.io/badge/python-3.6-blue.svg)](https://badge.fury.io/py/LabPype)

* [What is LabPype?](#What-is-LabPype)
* [Getting Started](#Getting-Started)
* [Examples](https://ncbi-hackathons.github.io/LabPype/)
* [Documentation](https://github.com/NCBI-Hackathons/LabPype/wiki)
    * [How to install](https://github.com/NCBI-Hackathons/LabPype/wiki/How-to-install)
    * [How to use](https://github.com/NCBI-Hackathons/LabPype/wiki/How-to-use)
    * [How to develop](https://github.com/NCBI-Hackathons/LabPype/wiki/How-to-develop)
    * [Class reference](https://github.com/NCBI-Hackathons/LabPype/wiki/Class-reference)
* [Concept](#Concept)
* [For Users](#For-Users)
* [For Developers](#For-Developers)
* [Contributing](#Contributing)
* [Future Plans](#Future-Plans)

### What is LabPype

LabPype provides a solution for rapid development of pipeline and workflow management software. A visualized pipeline software provides features such as reusability of workflows, user-friendly interface, and highly integrated functionalities. LabPype accelerates the making of such software for developers. It also helps the scientists become the developers to meet their increasing and diverging needs.

LabPype is a software and a framework implemented in pure Python language. As a software, LabPype helps you efficiently create highly interactive workflows. As a framework, LabPype tries to minimize the efforts needed to make new widgets.

### Getting Started

To quickly get started, use pip to install LabPype:

    pip install labpype

To update Labpype and it's dependencies:

    pip install -U labpype

Then, to run LabPype:

    python -m labpype.__init__

In the main windows, click the button that looks like a wrench on the top left to bring up the package manage dialog. Click "Download from repository", then click "OK" without changing the url in the text box to download the toy widget set.

#### Dependencies
* Python (>= 3.5)
* wxPython (>= 3.0.3)
* [DynaUI](https://github.com/yadizhou/DynaUI)

### Concept
![Concept](assets/img/concept.png)

### For Users
A visualized pipeline software has many advantages:
* Centralized. There is less need to switch between multiple programs. Data management and processing are integrated.
* Visualized. It allows users to focus on the experiment logic, and saves users from having to use command lines.
* Interactive. Users can try different workflows, inputs, and parameters, and can get feedback in real time.
* Extensible. Functions can be extended by user-developed widgets.
* Reusable. Workflows (or part of the workflow) can be reused to reduce repetitive tasks.
* Sharable. Workflows can be shared.

Users draw a workflow by adding and linking the widgets, and set input for the data widgets or the parameters for the task widgets using their dialogs. Then users can choose to run certain tasks manually, or just run the final task. Widgets will automatically trace back to determine what upstream tasks need to be done first. The results can be either displayed in the task widget's dialog, or in specialized output widgets.
:point_right:[See here for examples.](https://ncbi-hackathons.github.io/LabPype/):point_left:

### For Developers
LabPype tries to minimize the efforts of developers to make a widget-based pipeline software. It handles things such as GUI, resource management, workflow logic, etc., that are universal in pipeline software. It exposes two main base classes, "widget" and "dialog", to developers. The base widget class knows how to act in a workflow. Developers just need to subclass it, specify a few attributes, and implement the task it does. Each widget may have an associated dialog for interaction. The base dialog class has many APIs for easy creation of various UI elements.

* Subclassing of `Widget` and `Dialog` is simple and flexible.
* Widget tasks can run in parallel using either multithreading or multiprocess.
* Dialogs can be generated automatically, meaning no coding needed for the look and interaction of dialogs.
* GUI is fully implemented and is ready to use. Color/font/image are customizable.
* Efficient resource management.

#### Examples for making widgets
Let's use summation of numbers as our toy example. The input widget's data type is number, and the task widget simply sum all the numbers passed to it and display the result. Here is the code for the two widgets.

Code in `mywidgetpackage/mywidget.py`:
```python
class ANCHOR_NUMBER(ANCHOR_REGULAR): pass
class ANCHOR_NUMBERS(ANCHOR_REGULAR): pass

class Number(Widget):
    NAME = "Number"
    DIALOG = "V"
    INTERNAL = FloatField(key="NUMBER", label="Number")
    OUTGOING = ANCHOR_NUMBER

    def Task(self):
        return self["NUMBER"]

class Summer(Widget):
    NAME = "Summer"
    INCOMING = ANCHOR_NUMBERS, "NUMBERS", True, "L"
    OUTGOING = ANCHOR_NUMBER

    def Task(self):
        return sum(self["NUMBERS"])
```

It's simple to make the `Summer` run in a separate thread (it sleeps for 0.5s after adding each number to mimic long running tasks):
```python
class Summer(Widget):
    ...
    THREAD = True

    def Task(self):
        p = 0
        for i in self["NUMBERS"]:
            time.sleep(0.5)
            self.Checkpoint()
            p += i
        return p
```

It can also run in another process. See the code in the toy widget set for more examples.


### Contributing
Thank you for being interested in contributing. Please contact the author if you would like to add features to the framework, or develop widgets for certain areas such as bioinformatics and data science.

### Future Plans
Add database support
