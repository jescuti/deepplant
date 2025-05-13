import json
import os
from pathlib import Path

###################################################
# STEP ONE: run 'pip install kaggle' in the terminal
###################################################


###################################################
# STEP TWO: swap with your Kaggle API username + key
# make a Kaggle account, & then you can generate a key in settings
###################################################
api_key = {
    'username': "USER_NAME",
    'key': "API_KEY"
}

kaggle_dir = Path.home() / '.kaggle'
os.makedirs(kaggle_dir, exist_ok = True)

kaggle_json_path = kaggle_dir / 'kaggle.json'
with open(kaggle_json_path, 'w') as handle:
    json.dump(api_key, handle)

os.chmod(kaggle_json_path, 0o600)

from kaggle.api.kaggle_api_extended import KaggleApi

dataset = "ashleywoertz2/deep-plant"
download_path = "."

api = KaggleApi()
api.authenticate()
api.dataset_download_files(dataset, path = download_path, unzip = True)

print(f"dataset downloaded and extracted to: {download_path}")

###################################################
# STEP THREE: run with 'python download_kaggle_dataset.py' :)
# ran for ~8 minutes on my laptop
###################################################