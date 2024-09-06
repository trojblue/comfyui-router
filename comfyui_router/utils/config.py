import os
import click
from omegaconf import OmegaConf
import GPUtil


CONFIG_PATH = os.path.expanduser("~/.comfyui_router/config.yaml")


def _get_default_cuda_devices():
    """Determine the default CUDA devices based on the number of available GPUs."""
    gpus = GPUtil.getGPUs()
    # Default to [0] if no GPU is detected or just one is available
    return list(range(len(gpus))) if gpus else [0]


_default_config = {
    "BROKER_URL": "amqp://user:password@host:port//",
    "COMFY_DIR": "/rmt/yada/apps/comfyui",
    "OUTPUT_DIR": "/lv0/comfy_outs",
    "START_PORT": 18188,
    "CUDA_DEVICES": _get_default_cuda_devices()
}


def _prompt_for_config(config, key, default_value):
    """Prompt user for configuration value based on the key."""
    if isinstance(default_value, list):
        default_value = ','.join(map(str, default_value))

    current_value = config.get(key, default_value)

    if key == "CUDA_DEVICES":
        current_value = ",".join(map(str, current_value))

    value = click.prompt(
        f"Please enter the {key} [{current_value}]",
        default=current_value,
        show_default=False
    )

    if key == "CUDA_DEVICES":
        return list(map(int, value.replace(' ', '').split(',')))

    return type(_default_config[key])(value)


def _load_or_create_config():
    """Load existing configuration or create a new one with default values."""
    if os.path.exists(CONFIG_PATH):
        config = OmegaConf.load(CONFIG_PATH)
    else:
        config = OmegaConf.create(_default_config)
    return OmegaConf.to_container(config, resolve=True)


def _save_config(config_dict):
    """Save the updated configuration to a file."""
    updated_config = OmegaConf.create(config_dict)
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    OmegaConf.save(updated_config, CONFIG_PATH)
    click.echo(f"Configuration updated and saved to {CONFIG_PATH}")


def configure_comfyui():
    """Public function to configure the ComfyUI router settings."""
    config_dict = _load_or_create_config()

    for key, default_value in _default_config.items():
        config_dict[key] = _prompt_for_config(config_dict, key, default_value)

    _save_config(config_dict)


def get_config():
    """Retrieve the full configuration as a dictionary."""
    if os.path.exists(CONFIG_PATH):
        config = OmegaConf.load(CONFIG_PATH)
    else:
        raise FileNotFoundError(
            f"Configuration file not found at {CONFIG_PATH}. Please run 'crt configure' first.")

    # Convert OmegaConf object to a standard Python dictionary
    return OmegaConf.to_container(config, resolve=True)