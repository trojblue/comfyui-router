import os
import subprocess
import threading
from contextlib import ExitStack
from tqdm import tqdm

from comfyui_router.utils import get_router_config, get_logger

logger = get_logger(__name__)

def find_requirements_dirs(base_dir):
    """Find all subdirectories with a requirements.txt file."""
    return [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and os.path.exists(os.path.join(base_dir, d, 'requirements.txt'))
    ]


def install_requirements(requirements_dirs):
    """Install packages listed in requirements.txt for each subdirectory."""
    for directory in tqdm(requirements_dirs, desc="Installing requirements"):
        req_file = os.path.join(directory, 'requirements.txt')
        print(f"Installing requirements for folder {directory}...")
        subprocess.run(['pip', 'install', '-r', req_file], check=True)


def run_comfyui_instance(port, device, comfy_dir, output_dir):
    """Run a ComfyUI instance on a specific port and CUDA device."""
    command = [
        'python', f'{comfy_dir}/main.py',
        '--port', str(port),
        '--cuda-device', str(device),
        '--output-dir', output_dir
    ]
    process = subprocess.Popen(command)
    return process


def launch_comfyui_instances(comfy_dir, output_dir, start_port, cuda_devices, 
                             install_requirements_flag=True):

    # Step 2: Optionally install requirements
    base_directory = os.path.join(comfy_dir, 'custom_nodes')
    requirements_dirs = find_requirements_dirs(base_directory)
    
    if install_requirements_flag and requirements_dirs:
        install_requirements(requirements_dirs)
    elif install_requirements_flag:
        print("No subdirectories with requirements.txt found.")

    # Step 3: Start ComfyUI instances in separate threads
    processes = []
    with ExitStack() as stack:
        for device in cuda_devices:
            port = start_port + device
            print(f"Starting ComfyUI on port {port} with CUDA device {device}")
            process = run_comfyui_instance(port, device, comfy_dir, output_dir)
            processes.append(process)
            stack.callback(process.terminate)  # Ensure process terminates on exit

        # Wait for all processes to complete
        for process in processes:
            process.wait()


def launch_comfyuis(install_requirements_flag=True):
    # Step 1: Get the configuration
    config = get_router_config()
    logger.info(f"Launching ComfyUI with configuration: {config}")
    
    # Extract relevant configuration values
    comfy_dir = config["COMFY_DIR"]
    output_dir = config["OUTPUT_DIR"]
    start_port = config["START_PORT"]
    cuda_devices = config["CUDA_DEVICES"]

    # Launch ComfyUI instances
    launch_comfyui_instances(comfy_dir, output_dir, start_port, cuda_devices, 
                             install_requirements_flag=install_requirements_flag)


if __name__ == "__main__":
    launch_comfyuis(install_requirements_flag=False)