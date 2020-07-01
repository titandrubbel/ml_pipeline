import json
import joblib
import numpy as np
from azureml.core.model import Model

# Called when the service is loaded
def init():
    global model
    
    # Get the path to the registered model file and load it
    model_path = Model.get_model_path('willshersystems__ansible-sshd.json')
    model = json.load(model_path)

# Called when a request is received
def run(test):
    
    print(test)
    
    output_format = model["data"]
    
    #output_json = json.dump(output_format)
    
    return output_format

