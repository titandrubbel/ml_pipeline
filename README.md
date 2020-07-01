# Defect Prediction pipeline
This repository contains the Defect Prediction pipeline build upon Azure Machine Learning. 

## Main scripts 
- ml_pipeline.ipynb: The main Python Notebook to build, run and deploy the workspace, experiment and pipeline for the first time. It contains a reference to scripts used to run a pipeline step, the environment settings, computing targets and data objects used to parse between the different pipeline components.
- config.json: Provides the subscription id, resource group and workspace name ot create/connect to an Azure ML service workspce.

## Pipeline scripts
- github_cloner.py:
- repo_miner.py:
- cleaning.py:
- training.py:
- evaluate.py:

## Deployment scripts
- conda_dependencies.yml:
- scoring.py:
- container_image:
- aci_deployment.py:




