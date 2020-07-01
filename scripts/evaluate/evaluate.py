import warnings
import json
import numpy as np
import pandas as pd
from pandas import read_csv
import argparse
import shutil
import joblib
import os 
from azureml.core.model import Model
from azureml.core import Workspace
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.datastore import Datastore
from azureml.core.run import Run
import datetime

warnings.filterwarnings('ignore')

cli_auth = AzureCliAuthentication()
ws = Workspace.from_config(auth=Cli-auth)

parser = argparse.ArgumentParser(description = "Evaluate model and replace if better")

parser.add_argument("--repo_owner", type=str, required=True, metavar='', help="Parameter with defined reposotiry owner")
parser.add_argument("--repo_name", type=str, required=True, metavar='', help="Parameter with defined repository name")
parser.add_argument("--train_model", type=str, required=True, metavar='', help="Json file with model")
parser.add_argument("--final_model", type=str, required=True, metavar='', help="Json file with the best model")

args = parser.parse_args()

run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace

timestamp_id = datetime.datetime.now()
time = timestamp_id.strftime("%m-%d-%Y-%H%M")

def get_pre_auc(path):
    last_model = os.listdir(path)[-1]
    with open(path+'/'+last_model, 'r') as model_file:
        model = json.load(model_file)
        pre_auc = model["data"][0]["mean_test_pr_auc"]
        
    return pre_auc, last_model

if not os.path.isdir(args.final_model):
    os.makedirs(args.final_model, exist_ok=True)

#get training accuracy and model name 
train_pre_auc, train_model_name = get_pre_auc(args.train_model)

#Get list will all models that are registered
model_list = Model.list(ws)

model_list
same_models =[]
for model in model_list:
    possible_name = args.repo_owner + "__"+args.repo_name
    if model.name[:len(possible_name)] ==possible_name:
        same_models.append(model)

#If model already in production check preduction accuracy 
if len(same_models) > 0:
    print("There is already a model in production")
    
    #Assume that the model in production is the most recent model
    production_model = next(
        filter(
            lambda x: x.created_time == max(model.created_time for model in model_list),
            model_list,
        )
    )
    
    production_pre_auc = float(production_model.tags.get('auc'))
    
    #If new trained model preduction accuracy is higher replace model        
    if train_pre_auc>production_pre_auc:
        #remove file in final folder
        model = Model.register(model_path=args.train_model+'/'+train_model_name,  
            model_name=args.repo_owner+'__'+args.repo_name,  # this is the name the model is registered as
            tags={"repo name": args.repo_name, "repo owner": args.repo_owner, "type": "decision tree", "auc": train_pre_auc, "time": time},
            description="Decision tree model for {}/{} repository".format(args.repo_owner, args.repo_name),
            workspace=ws)
        
        # Get the blob storage associated with the workspace
        pipeline_datastore = Datastore(ws, "datastore_pipeline")

        #Upload production model to main blob folder
        pipeline_datastore.upload_files([args.train_model+'/'+train_model_name], target_path="production_model"+'/'+args.repo_owner+'/'+args.repo_name, overwrite=True)
        
        shutil.copyfile(args.train_model+'/'+train_model_name, args.final_model+'/'+train_model_name)
        
        print("New trained model performs better and replaced the model in production")

        
    #If production model prediction accuracy is higher do nothing
    else:
        print("Production model performs better")
        
#If no model in production place trained model in registry folder
if len(same_models) == 0:
    run.log(name="mean_test_pr_auc", value=train_pre_auc)
    print("This is the first model that is trained")
        
    model = Model.register(model_path=args.train_model+'/'+train_model_name,  
        model_name=args.repo_owner+'__'+args.repo_name,  # this is the name the model is registered as
        tags={"repo name": args.repo_name, "repo owner": args.repo_owner, "type": "decision tree", "auc": train_pre_auc, "time": time},
        description="Decision tree model for {}/{} repository".format(args.repo_owner, args.repo_name),
        workspace=ws)
    

    # Get the blob storage associated with the workspace
    pipeline_datastore = Datastore(ws, "datastore_pipeline")

    #Upload production model to main blob folder
    pipeline_datastore.upload_files([args.train_model+'/'+train_model_name], target_path="production_model"+'/'+args.repo_owner+'/'+args.repo_name, overwrite=True)
    
    shutil.copyfile(args.train_model+'/'+train_model_name, args.final_model+'/'+train_model_name)
    
    print("Trained model is placed in production!")