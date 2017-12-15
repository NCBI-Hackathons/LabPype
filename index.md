# LabPype
LabPype is a software and a framework implemented in pure Python language.

As a software, LabPype helps you efficiently create highly interactive workflows.
It is based on the idea that a workflow consists of a series of widgets, each representing a type of data or task that can be executed.
LabPype lets you reuse the tasks or data in a previous workflow to construct new workflows with minimal repetition.
When designing your lab tasks, whether dry or wet, you can benefit from using LabPype with a suitable set of widgets. 

As a framework, LabPype tries to minimize the efforts needed to make new widgets.
It handles things such as GUI, resource management, workflow logic, etc., that are universal in pipeline software.
It exposes two main base classes to developers. The base widget class knows how to act in a workflow.
Developers just need to subclass it, specify a few attributes, and implement the task it does, or wrap a function that is already implemented.
Each widget may have an associated dialog for interaction. The base dialog class has many APIs to simplify the creation of various UI elements.

We are going to see four examples here.
The first example demonstrates the basic idea of LabPype and how to develop widgets using LabPype.
The second example shows how it assists the design of a specific wet lab experiment.
The third example demonstrates its flexibility by combining widgets.
The last example shows three main ways to implement tasks in LabPype.

<br>

### Example 1: Toy widget set

This toy widget set demonstrates the basic ideas of LabPype. Each widget has several anchors for making connections.
The output of a widget will be send to all the widgets that are connected to its output anchor (cyan rectangle).
When you run a downstream task, LabPype will schedule all the upstream tasks and perform them.
When you change the data of a widget, all downstream tasks will be reset.
Tasks can run in a separate thread so that the GUI is not blocked, as is the case for the "Summer" and "Multiplier".
A widget can also start a subprocess, which is illustrated in "SubprocessSummer".
LabPype provides many features that make widget making efficient. Check out the source code of this widget set to learn more: [LabPype-ToyWidget](https://github.com/yadizhou/LabPype-ToyWidget).
A convenient way to install this widget set is to open the widget manage dialog, click "Download from repository", leave the url blank and click ok.

| Widget set | Example Workflow | Docked Dialogs |
| --- | --- | --- |
| ![toy0](assets/img/toy/0.png) | ![toy1](assets/img/toy/1.png) | ![toy2](assets/img/toy/2.png) |

There are several other widgets in this package:

| Widget | Dialog | Note |
| --- | --- | --- |
| ![toy3](assets/img/toy/3.png) | ![toy4](assets/img/toy/4.png) | "Clicker" is used for testing the stability of LabPype.<br>Add this widget to the canvas and run it. It will then randomly start/stop other widgets on the canvas. |
| ![toy5](assets/img/toy/5.png) | ![toy6](assets/img/toy/6.png) | This example shows how to use DataField as internal input type for automatic generation of dialogs.<br>[See source code](https://github.com/yadizhou/LabPype-ToyWidget/blob/b43b289f98da8f9df607ca8fbf8a0666df1309d0/toy/widget.py#L122) |
| ![toy7](assets/img/toy/7.png) | ![toy8](assets/img/toy/8.png) | This example shows how to define your own dialog and link the UI elements with the data of the widget.<br>[See source code](https://github.com/yadizhou/LabPype-ToyWidget/blob/b43b289f98da8f9df607ca8fbf8a0666df1309d0/toy/dialog.py#L17) |

<br>

### Example 2: Cloning widget set
The following workflow demonstrates the steps of how to use bimolecular fluorescence complementation to test the interaction between two proteins.
This workflow makes the experiment very intuitive. User can modify the input (e.g., primers, DNA sequences, enzymes, etc.) and simulate the experiment to get the hypothetical result in real time.

![cloning0](assets/img/cloning/0.png)

* This workflow gives a clear layout of the steps in this experiment.
* Users can interact with the widgets. For example, we can input the primers, choose what enzyme to use, etc.
* It simulates the PCR and digestion experiments, and gives the hypothetical sequences produced. If a mistake is made in the design of the primers, some downstream step will send a warning by showing that the job cannot be done.
* Besides simulating experiments, the widgets show additional information related to a particular step. For example, the Double Digest widget can show the suitable buffer for reaction for the two enzymes passed to it.
* For steps such as "Mini-Prep" and "Glycerol Stock", simulation isn't necessary; but instructions for those steps will show up in their dialogs.
* A workflow can be easily redesigned by changing the input of its widgets or replacing existing widgets with new ones. For example, we can replace the "cDNA" widget with an "Entrez Efetch" widget to directly get the sequence from GenBank.

| Widget/Workflow | Dialog | Note |
| --- | --- | --- |
| ![cloning3](assets/img/cloning/3.png) | ![cloning4](assets/img/cloning/4.png) | "DNA" lets you load a sequence file or directly input a sequence. |
| ![cloning5](assets/img/cloning/5.png) | ![cloning6](assets/img/cloning/6.png) | "Primer" lets you select a primer from a predefined prime database. |
| ![cloning7](assets/img/cloning/7.png) | ![cloning8](assets/img/cloning/8.png) | "Restriction Enzyme" lets you select a restriction enzyme from an internal RE database. |
| ![cloning1](assets/img/cloning/1.png) | ![cloning2](assets/img/cloning/2.png) | This workflow represents two PCR reactions that use the same set of primers and different templates. |

<br>

### Example 3: Biopython widget set
This example shows what users can do with just four widgets. These four widgets are simply wrappers for functions from Biopython package.
With LabPype, we can quickly write wrappers for functions from popular libraries.

| Widget set | Note |
| --- | --- |
| ![biopython0](assets/img/biopython/0.png) | **LoadFile** - load a FASTA or GenBank file, and sends sequence records to downstream widgets<br><br>**SaveFile** - save the records received from upstream widgets to either FASTA or GenBank file<br><br>**NewRecord** - let user input sequence directly<br><br>**ViewSequence** - show the sequences sent to it |

| Scheme | Task |
| --- | --- |
| ![biopython1](assets/img/biopython/1.png) | Show the sequence loaded from file |
| ![biopython2](assets/img/biopython/2.png) | Save input(s) to a sequence file<br>View the sequence |
| ![biopython3](assets/img/biopython/3.png) | Convert a file to another format |
| ![biopython4](assets/img/biopython/4.png) | Merge files |
| ![biopython5](assets/img/biopython/5.png) | Append a record to a file |

What we can do is not predetermined by what widgets we have. More importantly, it is determined by how we connect them.

<br>

### Example 4: Machine learning widget set
The tasks in this example were written in three different ways: tasks were directly implemented in the widget; widgets were wrappers for other libraries; widgets were wrapper for external tools.

| Widget set | Note |
| --- | --- |
| ![data0](assets/img/data/0.png) | |

**File** - specify a file path (does not load the file)
<br>**LoadData** - load a TSV/CSV/SVM format file
<br>**LRTrain** - train a linear regression model using directly implemented functions
<br>**LRPredict** - use a trained model to predict a new sample
<br>**PerceptronTrain** - train a perceptron model in a separate thread
<br>**PerceptronPredict** - predict a new sample using a perceptron model
<br>**LIBSVMTrain** - serve as an interface for the external svm-train.exe
<br>**LIBSVMPredict** - serve as an interface for the external svm-predict.exe
<br>**RegressionEvaluate** - show RMSE
<br>**ClassificationEvaluate** - show confusion matrix, accuracy, SE, SP, and AUC
<br>**PlotScatter** - make a scatter plot

A typical linear regression use case looks like this:  
![data1](assets/img/data/1.png)

Here we use the same training data to train the perceptron model using three different kernels, and evaluate the results using a test data set.  
![data2](assets/img/data/2.png)

This example is basically equal to directly call the svm-train and svm-predict. However, we can reuse the file path or the modeling parameters.
In addition, the "LIBSVMPredict" not only calls the svm-predict, but also loads the predicted results once its done so that evaluation can be done just like the perceptron case.  
![data3](assets/img/data/3.png)
