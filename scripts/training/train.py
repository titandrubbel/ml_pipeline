import joblib
import json
import numpy as np
import pandas as pd
from pandas import read_csv
import walk_forward_release
import os
from azureml.core.model import Model
from azureml.core import Workspace
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.run import Run
from azureml.core.datastore import Datastore

import argparse
import datetime

import warnings
warnings.filterwarnings('ignore')

parser = argparse.ArgumentParser(description = "Train model on metrics data")


parser.add_argument("--repo_owner", type=str, required=True, metavar='', help="Parameter with defined reposotiry owner")
parser.add_argument("--repo_name", type=str, required=True, metavar='', help="Parameter with defined repository name")
parser.add_argument("--metrics_clean", type=str, required=True, metavar='', help="csv file with cleaned metrics")
parser.add_argument("--train_model", type=str, required=True, metavar='', help="Json file with trained model")

args = parser.parse_args()

run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace


data = pd.read_csv(args.metrics_clean+'/'+"metrics_clean.csv")
data = data[data.repo == args.repo_owner+'/'+args.repo_name].fillna(0)


# Create column to group files belonging to the same release (identified by the commit hash)
data['group'] = data.commit.astype('category').cat.rename_categories(range(1, data.commit.nunique()+1))

# Make sure the data is sorted by commit time (ascending)
data.sort_values(by=['committed_at'], ascending=True)
data = data.reset_index(drop=True)
data = data.drop(['commit', 'committed_at', 'filepath', 'repo', 'path_when_added', 'tokens'], axis=1)

# Train
X, y = data.drop(['defective'], axis=1), data.defective.values.ravel()


for model in ['decision_tree']:

    # Train
    cv_results, best_index = walk_forward_release.learning(X, y, walk_forward_release.models[model], walk_forward_release.search_params[model])

    cv_results = pd.DataFrame(cv_results).iloc[[best_index]] # Take only the scores at the best index
    cv_results['n_features'] = X.shape[1]
    cv_results['y_0'] = y.tolist().count(0)
    cv_results['y_1'] = y.tolist().count(1)
    
    print(cv_results["mean_test_pr_auc"].to_string(index=False))
    run.log(name="mean_test_pr_auc", value=cv_results["mean_test_pr_auc"].to_string(index=False))    
    
    
    
    if not os.path.isdir(args.train_model):
        os.makedirs(args.train_model, exist_ok=True)
        
    timestamp_id = datetime.datetime.now()
    time = timestamp_id.strftime("%m-%d-%Y_%H%M")
    
    model_name = "{}__{}.json".format(args.repo_owner, args.repo_name) 
    output_path = os.path.join(args.train_model, model_name)

    with open(output_path, 'w') as outfile:
        cv_results.to_json(outfile, orient='table', index=False)    
    
    
    # Get the blob storage associated with the workspace
    pipeline_datastore = Datastore(ws, "datastore_pipeline")

    #Upload production model to main blob folder
    pipeline_datastore.upload_files([args.train_model+'/'+model_name], target_path="train_model"+'/'+args.repo_owner+'/'+args.repo_name+'/'+time, overwrite=True)
    
print("Model is trained!")