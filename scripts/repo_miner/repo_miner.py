from git import Repo
import os
import git
import argparse

import iacminer
from pydriller import GitRepository
from datetime import datetime
from iacminer.miners.github import GithubMiner
from iacminer.miners.repository import RepositoryMiner
import nltk 
import warnings
import json
import numpy as np
import pandas as pd
from pandas import read_csv
import csv
nltk.download('stopwords')
nltk.download('punkt')

from azureml.core.run import Run
from azureml.core.model import Model
from azureml.core import Workspace

parser = argparse.ArgumentParser("A repository miner which gets metrics from cloned github repos")

parser.add_argument("--repo_owner", type=str, required=True, metavar='', help="Parameter with defined reposotiry owner")
parser.add_argument("--repo_name", type=str, required=True, metavar='', help="Parameter with defined repository name")
parser.add_argument("--raw_data", type=str, required=True, metavar='', help="Cloned github repo data")
parser.add_argument("--metrics_data", type=str, required=True, metavar='', help="csv file with metrics")

args = parser.parse_args()

run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace


access_token = os.getenv("GITHUB_KEY", "<my-account-key>")

#make sure it on up-to-date with master
os.popen('cd '+args.raw_data +'/'+ args.repo_owner+'/'+ args.repo_name+' && git checkout master').close()

miner = RepositoryMiner(token = access_token,
                       path_to_repo=args.raw_data +'/'+ args.repo_owner+'/'+ args.repo_name)


if not os.path.isdir(args.metrics_data):
    os.makedirs(args.metrics_data, exist_ok=True)
      
file_name = "metrics.csv"
output_path = os.path.join(args.metrics_data, file_name)

data = pd.DataFrame()
for metrics in miner.mine():
    data = data.append(metrics, ignore_index=True)

with open(output_path, 'w') as outfile:
    data.to_csv(outfile, index=False)
    
print("Metrics created!!")
