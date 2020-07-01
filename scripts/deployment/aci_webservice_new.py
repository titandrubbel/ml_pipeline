import os, json, sys
import argparse
import os
from azureml.core import Workspace
from azureml.core.image import ContainerImage, Image
from azureml.core import Run
from azureml.core.model import Model
from azureml.core.authentication import AzureCliAuthentication
from azureml.core.webservice import Webservice
from azureml.core.model import InferenceConfig
from azureml.core.environment import Environment
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.webservice import AciWebservice
from azureml.core import Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.datastore import Datastore


#cli_auth = AzureCliAuthentication()
#interactive_auth = InteractiveLoginAuthentication(tenant_id="910b2b66-da11-4e98-a342-699afc4d5b62")
#cli_auth = AzureCliAuthentication()
#ws = Workspace.from_config(auth=interactive_auth)
ws = Workspace.from_config('./')

parser = argparse.ArgumentParser("The model deployment to container image")

parser.add_argument("--repo_owner", type=str, required=True, metavar='', help="Parameter with defined reposotiry owner")
parser.add_argument("--repo_name", type=str, required=True, metavar='', help="Parameter with defined repository name")
parser.add_argument("--final_model", type=str, required=True, metavar='', help="Cloned github repo data")
parser.add_argument("--aci_store", type=str, required=True, metavar='', help="JSON file with image information")

args = parser.parse_args()

run = Run.get_context()
exp = run.experiment
ws = run.experiment.workspace

print(os.listdir(args.final_model))
print(args.final_model+'/'+"{}__{}.json".format(args.repo_owner,args.repo_name))

try:
    with open(args.final_model+'/'+"{}__{}.json".format(args.repo_owner,args.repo_name)) as f:
        image_model = json.load(f)
except:
    print("No new model to register thus no need to create new scoring image")
    # raise Except
    
service_name = 'aci-service'

# Remove any existing service under the same name.
try:
    Webservice(ws, service_name).delete()
except WebserviceException:
    pass

inference_config = InferenceConfig(runtime= "python",
                                   entry_script="scoring.py",
                                   conda_file="conda_dependencies.yml")

aci_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=1)

#Get most recent model
model_list = Model.list(ws)
production_model = next(
    filter(
        lambda x: x.created_time == max(model.created_time for model in model_list),
        model_list,
    )
)

model = Model(ws, name=production_model.name)
model

service = Model.deploy_from_model(workspace=ws,
                       name=service_name,
                       models=[model],
                       inference_config=inference_config,
                       deployment_config=aci_config)

service.wait_for_deployment(show_output=True)

aci_webservice = {}
aci_webservice["aci_name"] = service.name
aci_webservice["aci_url"] = service.scoring_uri
with open(args.aci_store+"/aci_webservice.json", "w") as outfile:
    json.dump(aci_webservice, outfile)

# Get the blob storage associated with the workspace
pipeline_datastore = Datastore(ws, "datastore_pipeline")

#Upload production model to main blob folder
pipeline_datastore.upload_files([args.aci_store+"/aci_service.json"], target_path="webservice"+'/'+args.repo_owner+'/'+args.repo_name, overwrite=True)
    
print("Deployed ACI Webservice: {} \nWebservice Uri: {}".format(service.name, service.scoring_uri)
    
