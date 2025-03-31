import click

from comfyui_router.utils.config import configure_comfyui
from comfyui_router.launchers.launch_comfyuis import launch_comfyuis


@click.group()
def cli():
    pass


@cli.command()
def configure():
    """Configure the ComfyUI router settings."""
    configure_comfyui()


@cli.command()
@click.option('--reinstall-requirements', is_flag=True, help="Reinstall requirements for custom nodes.")
def launch_comfy(reinstall_requirements):
    """Launch ComfyUI instances based on the configuration."""

    # Load the configuration
    launch_comfyuis(install_requirements_flag=reinstall_requirements)
    click.echo("ComfyUI instances launched successfully.")


if __name__ == "__main__":
    cli()
