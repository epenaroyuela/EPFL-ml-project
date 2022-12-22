# EPFL Machine Learning - Project II: Worm tracking for personality detection
Code for the project work for **CS-433 Machine Learning** at EPFL
## Authors: Guillem Bartrina Moreno, Aitor Ganuza Izagirre, Eduardo Peña Royuela

This readme does not provide a detailed description of the functions, for a more in-depth description, please check the comments on the corresponding files.

## Reproducibility
To reproduce our results, follow these steps:

### Acquire the data
Download the project data from this link [https://drive.switch.ch/index.php/s/FUupj8ht776nY3j] and place it in the **data** folder. 

### Install the requirements
Install the required packages by running ```pip install -r requirements.txt```

### Execution
Run ```python3 ./worm_tracker.py -I capture.avi [-O labels.txt] [-L true_labels.txt] [-A annotated_capture.avi]```, where:

- Argument ```-I capture.avi``` specifies the path to the input video
- Optional argument ```-O labels.txt``` specifies the path in which the tracking labels will be written
- Optional argument ```-L true_labels.txt``` specifies the path of the true labels, to compute and print the evaluation
- Optional argument ```-A annotated_capture.avi``` specifies the path in which to write the input video with the tracking annotations

_At least one of the optional arguments is required_

## Project structure
The structure of this repository is the following:

### root
The root contains the **worm_tracker.py** script, the **requirements.txt** file and **defalut_configuration.yaml**, which contains the default configuration for the tracking script.

### src
This folder contains all the python source files with the different functions and classes developed for the project, used by the **worm_tracker.py** script.

### papers
This folder contains a compilation of the papers consulted for the realization of this project. They are also cited in the report delivered.

### notebooks
This folder contains various jupyter notebooks where data exploration and preprocessing has been conducted as well as different tests and checks for the development of this project. 

### tests
This folder contains files of different tests carried out during the project. 

### data
This folder must contain the project data. To be downloaded from: https://drive.switch.ch/index.php/s/FUupj8ht776nY3j