# EPFL Machine Learning - Project II
Code for the project work for **CS-433 Machine Learning** at EPFL
## Authors: Guillem Bartrina Moreno, Aitor Ganuza Izagirre, Eduardo Peña Royuela

This readme does not provide a detailed description of the functions, for a more in-depth description, please check the comments on the corresponding files.

## Reproducibility
To reproduce our results, go through the steps below:

### Acquire the data
Download the project data from this link and put it in the *data* folder. Link: https://drive.switch.ch/index.php/s/FUupj8ht776nY3j

### Install the requirements
To install the requirements for this project run ```pip install -r requirements.txt```

### Execution
When executing the code there are several options depending on what you want to do. 

Run 
```python3 worm_tracker.py -I capture.avi -O labels.txt -A capture_annotated.avi ```

where 

## Project structure
The structure of this repository is the following:

### root
This folder contains the worm_tracker.py script and the project configuration files

### papers
Contains a compilation of the papers consulted for the realization of this project.

### notebooks
Various Jupyter notebooks where data exploration was conducted as well as various tests for the development of this project.

### src
In this folder are all the python source files with the different options and classes defined for the project

### tests
This folder contains files of different tests carried out for the progress of the project.

### data
In this folder you must save the project data previously downloaded from the link: https://drive.switch.ch/index.php/s/FUupj8ht776nY3j