import os
import click
from omegaconf import OmegaConf

CONFIG_PATH = os.path.expanduser("~/.comfyui_router/config.yaml")

@click.group()
def cli():
    pass

@cli.command()
def configure():
    """Configure the ComfyUI router credentials."""
    
    # Load existing configuration if it exists
    if os.path.exists(CONFIG_PATH):
        config = OmegaConf.load(CONFIG_PATH)
    else:
        config = OmegaConf.create({})

    # Retrieve the existing BROKER_URL or set it to a placeholder
    existing_broker_url = config.get("BROKER_URL", "amqp://user:password@host:port//")

    # Prompt the user, displaying the existing BROKER_URL if available
    broker_url = click.prompt(
        f"BROKER_URL [{existing_broker_url}]", 
        default=existing_broker_url,
        show_default=False  # Display the default value in the prompt
    )

    # Update or add the BROKER_URL
    config.BROKER_URL = broker_url

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    # Write the updated configuration back to the file
    OmegaConf.save(config, CONFIG_PATH)

    click.echo(f"Configuration updated and saved to {CONFIG_PATH}")

@cli.command()
def test():
    print("Test")

if __name__ == "__main__":
    cli()
