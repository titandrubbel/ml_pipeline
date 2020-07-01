# Defect Prediction pipeline
This repository contains the script used to build the Defect Prediction pipeline build upon Azure Machine Learning. 

## Main scripts 
- ml_pipeline.ipynb: The main Python Notebook to build, run and deploy the workspace, experiment and pipeline for the first time. It contains a reference to scripts used to run a pipeline step, the environment settings, computing targets and data objects used to parse between the different pipeline components.
- config.json: Provides the subscription id, resource group and workspace name ot create/connect to an Azure ML service workspce.

## Pipeline scripts
- github_cloner.py: Reads the arguments and clones the corresponding repository into the blobstore
- repo_miner.py: Reads the cloned GitHub data and extracts metrics which will be saved as a csv file into the blobstore
- cleaning.py: Removes useless oberservations from the produced metrics and saves the cleaned metrics as a csv file into the blob store
- training.py: Consumes the cleaned metrics and runs a binary classification model (decision tree) making use of the walk-foward_relase.py file which provides the code to train the model
- evaluate.py: Evaluates the trained model with the model in production. If the production model performs better the below steps are skipped

## Deployment scripts
- conda_dependencies.yml: The file contains the list of dependencies to prepare the environment needed for scoring.py
- scoring.py: 
- container_image.py: Takes the model from the evaulate step (if there is any) and creates a docker image and publishes it.
- aci_deployment.py:  Takes the docker image frmo the previous step and creates an aci cluster and deploys the web service on it




