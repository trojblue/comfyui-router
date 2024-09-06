# logging_config.py
import logging
from rich.logging import RichHandler

# Configure logging with RichHandler
logging.basicConfig(
    level=logging.INFO,  # Set the default logging level
    format="%(message)s",  # Define the log message format
    datefmt="[%X]",  # Define the date format
    handlers=[RichHandler()]  # Use RichHandler for pretty logs
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    if not name:
        name = "comfyui_router"
        
    return logging.getLogger(name)
