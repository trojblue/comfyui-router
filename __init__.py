"""
@author: BennyKok
@title: comfyui-deploy
@nickname: Comfy Deploy
@description: 
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

import inspect
import sys
import importlib
import subprocess
import requests
import folder_paths
from folder_paths import add_model_folder_path, get_filename_list, get_folder_paths
from tqdm import tqdm

from rich import print
from comfy.cli_args import args


from comfyui_router.utils import get_router_config
from comfyui_router.launchers.launch_workers import start_celery_worker

from concurrent.futures import ThreadPoolExecutor

worker_executor = ThreadPoolExecutor(max_workers=1)

config = get_router_config()
broker_url = config.get("BROKER_URL", "")

if broker_url:
    print(f"Celery worker starting on port: {args.port}")

    worker_executor.submit(
        start_celery_worker, broker_url, args.port
    )
else:
    print("No broker URL provided, Celery worker not started.")


# from . import custom_routes
# import routes

ag_path = os.path.join(os.path.dirname(__file__))

def get_python_files(path):
    return [f[:-3] for f in os.listdir(path) if f.endswith(".py")]

def append_to_sys_path(path):
    if path not in sys.path:
        sys.path.append(path)

paths = ["comfy-nodes"]
files = []

for path in paths:
    full_path = os.path.join(ag_path, path)
    append_to_sys_path(full_path)
    files.extend(get_python_files(full_path))

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# Import all the modules and append their mappings
for file in files:
    module = importlib.import_module(file)

    if hasattr(module, "NODE_CLASS_MAPPINGS"):
        NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
    if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
        NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

WEB_DIRECTORY = "web-plugin"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]