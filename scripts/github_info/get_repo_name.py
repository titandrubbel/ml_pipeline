import argparse
import os

parser = argparse.ArgumentParser("A github miner, clones the input github repo")

parser.add_argument("--github_list", type=str, required=True, metavar='', help="Text file with URL of GitHub repo")
parser.add_argument("--repo_name", type=str, required=True, metavar='', help="The name of the GitHub repository")
parser.add_argument("--repo_owner", type=str, required=True, metavar='', help="The owner of the GitHub repository")

args = parser.parse_args()


for line in open(args.github_list,'r'):
    github_url = line.split("github.com/")[1].split("/")
    repo_owner, repo_name = github_url[0], github_url[1]
    
args.repo_name = repo_name
print(args.repo_name)
args.repo_owner = repo_owner
print(args.repo_owner)



    
