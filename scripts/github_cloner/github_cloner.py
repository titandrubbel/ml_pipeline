from git import Repo
import os
import git
import argparse
import warnings
from azureml.core.run import Run
from azureml.core.model import Model
from azureml.core import Workspace

parser = argparse.ArgumentParser("A github miner, clones the input github repo")

parser.add_argument("--github_list", type=str, required=True, metavar='', help="Text file with URL of GitHub repo")
parser.add_argument("--repo_owner", type=str, required=True, metavar='', help="Parameter with defined reposotiry owner")
parser.add_argument("--repo_name", type=str, required=True, metavar='', help="Parameter with defined repository name")
parser.add_argument("--raw_data", type=str, required=True, metavar='', help="Cloned github repo data")

args = parser.parse_args()

run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace

#for line in open(args.github_list,'r'):
#    github_url = line.split("github.com/")[1].split("/")
#    repo_owner, repo_name = github_url[0], github_url[1]


git_url = 'https://github.com'+'/'+args.repo_owner+'/'+args.repo_name+'.git' 
print(git_url)

if not os.path.isdir(args.raw_data):
    os.makedirs(args.raw_data, exist_ok=True)     

Repo.clone_from(git_url, args.raw_data+'/'+args.repo_owner+'/'+args.repo_name)

print("Github data cloned in blob store")
