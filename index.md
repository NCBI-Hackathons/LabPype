# LabPype
LabPype is a software and a framework implemented in Python.

As a software, LabPype helps you create highly interactive workflows efficiently.
It is based on the idea that a workflow consists of a series of widgets, each representing a type of data or a task to be executed.
LabPype allows you to reuse the tasks or data from a previous workflow to construct new workflows with minimal repetition.

As a framework, LabPype tries to minimize the efforts needed to make new widgets.
It handles GUI, resource management, workflow logic, etc., that are universal in pipeline software.
It provides two main base classes to developers. The base widget class knows how to act in a workflow.
To make a new widget, a developer just need to subclass the base widget, specify a few attributes, and implement its task, or wrap an already implemented function.
Each widget may have an associated dialog for user interaction. The base dialog class has many APIs to simplify the creation of various UI elements.

We are going to see four examples here.
The first example demonstrates the basic idea of LabPype and how to develop widgets using LabPype.
The second example shows how it assists the design of a specific wet lab experiment.
In the third example, several widgets are combined in different ways to illustrate the flexibility of LabPype.
The last example shows three main ways to implement tasks in LabPype.

<br>

### Example 1: Toy widget set

This toy widget set shows the basic ideas of LabPype. Each widget has several anchors for making connections.
The output of a widget will be sent to all the widgets that are connected to its output anchor (cyan rectangle).
When you run a downstream task, LabPype will schedule all the upstream tasks and perform them.
When you change the data of a widget, all downstream tasks will be reset.
Tasks can run in a separate thread to avoid blocking the GUI (See "Summer" and "Multiplier").
A widget can also start a subprocess, which is illustrated in "SubprocessSummer".
LabPype provides many features that make widget making efficient. Check out the source code of this widget set to learn more: [LabPype-ToyWidget](https://github.com/yadizhou/LabPype-ToyWidget).
A convenient way to install this widget set is to open the widget manage dialog, click "Download from repository", leave the url blank and click ok.

| Widget set | Example Workflow | Docked Dialogs |
| --- | --- | --- |
| ![toy0](assets/img/toy/0.png) | ![toy1](assets/img/toy/1.png) | ![toy2](assets/img/toy/2.png) |

Here are some other widgets in this package:

| Widget | Dialog | Note |
| --- | --- | --- |
| ![toy3](assets/img/toy/3.png) | ![toy4](assets/img/toy/4.png) | "Clicker" is used for testing the stability of LabPype.<br>Add this widget to the canvas and run it. It will constantly start/stop other widgets on the canvas in a fast and random fashion. |
| ![toy5](assets/img/toy/5.png) | ![toy6](assets/img/toy/6.png) | This example shows how to use DataField as internal input type for automatic generation of dialogs.<br>[See source code](https://github.com/yadizhou/LabPype-ToyWidget/blob/b43b289f98da8f9df607ca8fbf8a0666df1309d0/toy/widget.py#L122) |
| ![toy7](assets/img/toy/7.png) | ![toy8](assets/img/toy/8.png) | This example shows how to define your own dialog and link the UI elements with data in the widget.<br>[See source code](https://github.com/yadizhou/LabPype-ToyWidget/blob/b43b289f98da8f9df607ca8fbf8a0666df1309d0/toy/dialog.py#L17) |

<br>

### Example 2: Cloning widget set
The workflow below gives a clear layout of the steps in using bimolecular fluorescence complementation to test the interaction between two proteins.
This workflow makes the experiment design very intuitive. User can modify the input (e.g., primers, DNA sequences, enzymes, etc.) and simulate the experiment to get hypothetical results in real time.

![cloning0](assets/img/cloning/0.png)

* Users can interact with the widgets. For example, we can input the primers, choose what enzymes to use, etc.
* It simulates the PCR and digestion experiments, and gives the hypothetical sequences produced. If a mistake is made in the design of the primers, the downstream steps will send warnings showing that the job cannot be done.
* Besides simulating experiments, the widgets show additional information related to a particular step. For example, the "Double Digest" widget can show the proper buffer for reaction of the two enzymes passed to it.
* For steps such as "Mini-Prep" and "Glycerol Stock", simulation isn't necessary; but instructions for those steps will show up in their dialogs.
* A workflow can be easily redesigned by changing the input of its widgets or replacing existing widgets with new ones. For example, we can replace the "cDNA" widget with an "Entrez Efetch" widget to directly get the sequence from GenBank.

| Widget/Workflow | Dialog | Note |
| --- | --- | --- |
| ![cloning3](assets/img/cloning/3.png) | ![cloning4](assets/img/cloning/4.png) | "DNA" lets you load a sequence file or directly input a sequence. |
| ![cloning5](assets/img/cloning/5.png) | ![cloning6](assets/img/cloning/6.png) | "Primer" lets you select a primer from a predefined primer database. |
| ![cloning7](assets/img/cloning/7.png) | ![cloning8](assets/img/cloning/8.png) | "Restriction Enzyme" lets you select a restriction enzyme from an internal RE database. |
| ![cloning1](assets/img/cloning/1.png) | ![cloning2](assets/img/cloning/2.png) | This workflow represents two PCR reactions that use the same set of primers but different templates. |

<br>

### Example 3: Biopython widget set
This example shows what users can do with just four widgets. These four widgets are simply wrappers for functions from Biopython package.
With LabPype, we can quickly write wrappers for functions from popular libraries.
Check out the source code of this widget set to learn more: [LabPype-BioPype](https://github.com/yadizhou/LabPype-BioPype).

| Widget set | Note |
| --- | --- |
| ![biopython0](assets/img/biopython/0.png) | **LoadFile** - load a FASTA or GenBank file, and send sequence records to downstream widgets<br><br>**SaveFile** - save the records received from upstream widgets to either FASTA or GenBank file<br><br>**NewRecord** - let user input sequence directly<br><br>**ViewSequence** - show the sequences sent to it |

| Scheme | Task |
| --- | --- |
| ![biopython1](assets/img/biopython/1.png) | Show the sequence loaded from file |
| ![biopython2](assets/img/biopython/2.png) | Save input(s) to a sequence file<br>View the sequence |
| ![biopython3](assets/img/biopython/3.png) | Convert a file to another format |
| ![biopython4](assets/img/biopython/4.png) | Merge files |
| ![biopython5](assets/img/biopython/5.png) | Append a record to a file |

What we can do is not predetermined by what widgets we have. It is also determined by how we connect them.

<br>

### Example 4: Machine learning widget set
The tasks in this example were written in three different ways: tasks were directly implemented in the widget; widgets were wrappers for other libraries; widgets were wrappers for external tools.

| Widget set | Note |
| --- | --- |
| ![data0](assets/img/data/0.png) | **File** - specify a file path (does not load the file)<br>**LoadData** - load a TSV/CSV/SVM format file<br>**LRTrain** - train a linear regression model using directly implemented functions<br>**LRPredict** - use a trained model to predict a new sample<br>**PerceptronTrain** - train a perceptron model in a separate thread<br>**PerceptronPredict** - predict a new sample using a perceptron model<br>**LIBSVMTrain** - serve as an interface for the external svm-train.exe<br>**LIBSVMPredict** - serve as an interface for the external svm-predict.exe<br>**RegressionEvaluate** - show RMSE<br>**ClassificationEvaluate** - show confusion matrix, accuracy, SE, SP, and AUC<br>**PlotScatter** - create a scatter plot |

A typical case of using linear regression looks like this:  
![data1](assets/img/data/1.png)
<br>

Here we use the same training data to train the perceptron model with three different kernels, and evaluate the results by a test data set.  
![data2](assets/img/data/2.png)
<br>

This example is basically equal to directly calling the "svm-train" and "svm-predict". However, we can reuse the file path or the modeling parameters.
In addition, the "LIBSVMPredict" not only calls the "svm-predict", but also loads the predicted results once it's done; evaluation can be conducted following that, as in the perceptron case.  
![data3](assets/img/data/3.png)
