import numpy as np
import pandas as pd
from pandas import read_csv
import argparse
import os
from azureml.core.run import Run
from azureml.core.model import Model
from azureml.core import Workspace


parser = argparse.ArgumentParser(description = "Clean metrics data")

parser.add_argument("--repo_owner", type=str, required=True, metavar='', help="Parameter with defined reposotiry owner")
parser.add_argument("--repo_name", type=str, required=True, metavar='', help="Parameter with defined repository name")
parser.add_argument("--metrics_data", type=str, required=True, metavar='', help="csv file with metrics")
parser.add_argument("--metrics_clean", type=str, required=True, metavar='', help="Cleaned csv file with metrics data")

args = parser.parse_args()

run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace

data = pd.read_csv(args.metrics_data+'/'+'metrics.csv')
data = data[data.repo == args.repo_owner+'/'+args.repo_name].fillna(0)

if not os.path.isdir(args.metrics_clean):
    os.makedirs(args.metrics_clean, exist_ok=True)
      
file_name = "metrics_clean.csv"
output_path = os.path.join(args.metrics_clean, file_name)

clean_data = data[data.groupby('commit').defective.transform(lambda x: len(set(x.values)) == 2)]


with open(output_path, 'w') as outfile:
    clean_data.to_csv(outfile, index=False)
    
print("Metrics data cleaned!!")