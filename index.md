# LabPype
LabPype is a software and a framework implemented in pure Python language.

As a software, LabPype helps you efficiently create highly interactive workflows. It is based on the idea that a workflow consists of a series of widgets, each representing a type of data or task that can be executed. LabPype lets you reuse the tasks or data in a previous workflow to construct new workflows with minimal repetition. When designing your lab tasks, whether dry or wet, you can benefit from using LabPype with a suitable set of widgets. 

As a framework, LabPype tries to minimize the efforts needed to make new widgets. It handles things such as GUI, resource management, workflow logic, etc., that are universal in pipeline software. It exposes two main base classes to developers. The base widget class knows how to act in a workflow. Developers just need to subclass it, specify a few attributes, and implement the task it does, or wrap a function that is already implemented. Each widget may have an associated dialog for interaction. The base dialog class has many APIs to simplify the creation of various UI elements.

We are going to see four examples here. The first example demonstrates the basic idea of LabPype and how to develop widgets using LabPype. The second example shows how it assists the design of a specific wet lab experiment. The third example demonstrates its flexibility by combining widgets. The last example shows three main ways to implement tasks in LabPype.


#### Example 1: Toy widget set

| Widget set | Example Workflow | Docked Dialogs |
| --- | --- | --- |
| ![toy0](assets/img/toy/0.png) | ![toy1](assets/img/toy/1.png) | ![toy2](assets/img/toy/2.png) |

| Widget | Dialog | Explain |
| --- | --- | --- |
| ![toy3](assets/img/toy/3.png) | ![toy4](assets/img/toy/4.png) | TODO |
| ![toy5](assets/img/toy/5.png) | ![toy6](assets/img/toy/6.png) | TODO |
| ![toy7](assets/img/toy/7.png) | ![toy8](assets/img/toy/8.png) | TODO |


#### Example 2: Cloning widget set
The following workflow demonstrate the steps of how to use bimolecular fluorescence complementation to test the interaction between two proteins. This workflow makes the experiment very intuitive. User can modify the input (e.g., primers, DNA sequences, enzymes, etc.) and simulate the experiment to get the hypothetical result in real time.

![cloning0](assets/img/cloning/0.png)

* This workflow gives a clear layout of the steps in this experiment.
* Users can interact with the widgets. For example, we can input the primers, choose what enzyme to use, etc.
* It simulates the PCR and digestion experiments, and gives the hypothetical sequences produced. If a mistake is made in the design of the primers, some downstream step will send a warning by showing that the job cannot be done.
* Besides simulating experiments, the widgets show additional information related to a particular step. For example, the Double Digest widget can show the suitable buffer for reaction for the two enzymes passed to it.
* For steps such as "Mini-Prep" and "Glycerol Stock", simulation isn't necessary; but instructions for those steps will show up in their dialogs.
* A workflow can be easily redesigned by changing the input of its widgets or replacing existing widgets with new ones. For example, we can replace the "cDNA" widget with an "Entrez Efetch" widget to directly get the sequence from GenBank.

The following workflow represents two PCR reactions that use the same set of primers and different templates.  
![cloning1](assets/img/cloning/1.png)
![cloning2](assets/img/cloning/2.png)

![cloning3](assets/img/cloning/3.png) This "DNA" widget lets you load a sequence file or directly input some sequence.  
![cloning4](assets/img/cloning/4.png)

![cloning5](assets/img/cloning/5.png) This "Primer" widget lets you select a primer from a predefined prime database.  
![cloning6](assets/img/cloning/6.png)

![cloning7](assets/img/cloning/7.png) This "Restriction Enzyme" widget lets you select a restriction enzyme from an internal RE database.  
![cloning8](assets/img/cloning/8.png)


#### Example 3: Biopython widget set
This example shows what users can do with just four widgets:  

| Widget set | Function |
| --- | --- |
| ![biopython0](assets/img/biopython/0.png) | **LoadFile** - loads a FASTA or GenBank file, and sends sequence records to downstream widgets<br>**SaveFile** - saves the records received from upstream widgets to either FASTA or GenBank file<br>**NewRecord** - lets user input sequence directly<br>**ViewSequence** - shows the sequences sent to it |

These four widgets are simply wappers for functions from Biopython package.

| Task | Scheme |
| --- | --- |
| Show the sequence loaded from file | ![biopython1](assets/img/biopython/1.png) |
| Save input(s) to a sequence file<br>View the sequence | ![biopython2](assets/img/biopython/2.png) |
| Convert a file to another format | ![biopython3](assets/img/biopython/3.png) |
| Merge files | ![biopython4](assets/img/biopython/4.png) |
| Append a record to a file | ![biopython5](assets/img/biopython/5.png) |


#### Example 4: Machine learning widget set

![data0](assets/img/data/0.png)

![data1](assets/img/data/1.png)

![data2](assets/img/data/2.png)

![data3](assets/img/data/3.png)
