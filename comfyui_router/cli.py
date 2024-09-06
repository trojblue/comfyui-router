import os
import click
import GPUtil
from omegaconf import OmegaConf

CONFIG_PATH = os.path.expanduser("~/.comfyui_router/config.yaml")

# Determine the default CUDA devices based on the number of available GPUs
def get_default_cuda_devices():
    gpus = GPUtil.getGPUs()
    return list(range(len(gpus))) if gpus else [0]  # Default to [0] if no GPU is detected or just one is available

DEFAULT_CONFIG = {
    "BROKER_URL": "amqp://user:password@host:port//",
    "COMFY_DIR": "/rmt/yada/apps/comfyui",
    "OUTPUT_DIR": "/lv0/comfy_outs",
    "START_PORT": 18188,
    "CUDA_DEVICES": get_default_cuda_devices()
}

def prompt_for_config(config, key, default_value):
    """Prompt user for configuration value based on the key."""
    # Convert list to a comma-separated string for display
    if isinstance(default_value, list):
        default_value = ','.join(map(str, default_value))

    # Get the existing or default value from the config
    current_value = config.get(key, default_value)

    # Prompt the user with the current value as default
    value = click.prompt(
        f"Please enter the {key} [{current_value}]",
        default=current_value,
        show_default=False
    )

    # Convert back to list of integers if the field is CUDA_DEVICES
    if key == "CUDA_DEVICES":
        return list(map(int, value.replace(' ', '').split(',')))

    # Return the value as its original type
    return type(DEFAULT_CONFIG[key])(value)

@click.group()
def cli():
    pass

@cli.command()
def configure():
    """Configure the ComfyUI router settings."""

    # Load existing configuration if it exists
    if os.path.exists(CONFIG_PATH):
        config = OmegaConf.load(CONFIG_PATH)
    else:
        config = OmegaConf.create(DEFAULT_CONFIG)

    # Convert config to a dictionary for safe access
    config_dict = OmegaConf.to_container(config, resolve=True)

    # Dynamically prompt for all configuration keys
    for key, default_value in DEFAULT_CONFIG.items():
        config_dict[key] = prompt_for_config(config_dict, key, default_value)

    # Convert back to OmegaConf and save
    updated_config = OmegaConf.create(config_dict)

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    # Write the updated configuration back to the file
    OmegaConf.save(updated_config, CONFIG_PATH)

    click.echo(f"Configuration updated and saved to {CONFIG_PATH}")

@cli.command()
def test():
    print("Test")

if __name__ == "__main__":
    cli()
