import os
from rich import print


# ===== Launching celery worker during comfy init =====


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


# ===== Initializing custom nodes =====


import easy_nodes
easy_nodes.initialize_easy_nodes(default_category="ComfyUI Router", auto_register=True)

from .comfy_nodes import *  # noqa: F403, E402

# NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = easy_nodes.get_node_mappings()

# print("NODE_CLASS_MAPPINGS", NODE_CLASS_MAPPINGS)
# print("NODE_DISPLAY_NAME_MAPPINGS", NODE_DISPLAY_NAME_MAPPINGS)


# __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# Optional: export the node list to a file so that e.g. ComfyUI-Manager can pick it up.
# easy_nodes.save_node_list(os.path.join(os.path.dirname(__file__), "node_list.json"))