import os
import click

@click.group()
def cli():
    pass


@cli.command()
def test():
    print("Test")