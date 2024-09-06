import os
from omegaconf import OmegaConf

CONFIG_PATH = os.path.expanduser("~/.comfyui_router/config.yaml")

def get_config():
    """Retrieve the full configuration as a dictionary."""
    if os.path.exists(CONFIG_PATH):
        config = OmegaConf.load(CONFIG_PATH)
    else:
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}. Please run 'crt configure' first.")

    # Convert OmegaConf object to a standard Python dictionary
    return OmegaConf.to_container(config, resolve=True)