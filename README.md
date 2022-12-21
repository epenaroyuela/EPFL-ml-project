# EPFL Machine Learning - Project II
Code for the project work for **CS-433 Machine Learning** at EPFL
## Authors: Guillem Bartrina Moreno, Aitor Ganuza Izagirre, Eduardo Peña Royuela

This readme does not provide a detailed description of the functions, for a more in-depth description, please check the comments on the corresponding files.

## Reproducibility
To reproduce our results, go through this steps

### Acquire the data
Download the project data from this link and put it in the **data** folder. https://drive.switch.ch/index.php/s/FUupj8ht776nY3j

### Install the requirements
Install the requirements for this project runing ```pip install -r requirements.txt```

### Execution
Run  ```python3 worm_tracker.py -I capture.avi -O labels.txt -A capture_annotated.avi ```, where the option ```-I capture.avi``` is the input video where the tracking will be carried out, the option ``` -O labels.txt``` is the name of the output labels genereted by the script, and finally, the option ```-A capture_annotated.avi``` generates the video with the annotated pixel that tracks the worm.

## Project structure
The structure of this repository is the following:

### root
This folder contains the **worm_tracker.py** script, the **requirements.txt** file and **defalut_configuration.yaml**, that is the project configuration file.

### papers
This folder contains a compilation of the papers consulted for the realization of this project.

### notebooks
This folder contains various jupyter notebooks where data exploration was conducted as well as different tests for the development of this project.

### src
This folder contains all the python source files with the different options and classes defined for the project that the **worm_tracker.py** file uses.

### tests
This folder contains files of different tests carried out for the progress of the project.

### data
In this folder you must save the project data previously downloaded from the link: https://drive.switch.ch/index.php/s/FUupj8ht776nY3j