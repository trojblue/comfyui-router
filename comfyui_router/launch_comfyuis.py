import os
import subprocess
import threading
from contextlib import ExitStack
from tqdm import tqdm

COMFY_DIR = "/rmt/yada/apps/comfyui"
OUTPUT_DIR = "/lv0/comfy_outs"
START_PORT = 18188
CUDA_DEVICES = [0, 1, 2, 3, 4, 5, 6, 7]

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

def run_comfyui_instance(port, device):
    """Run a ComfyUI instance on a specific port and CUDA device."""
    command = [
        'python', f'{COMFY_DIR}/main.py',
        '--port', str(port),
        '--cuda-device', str(device),
        '--output-dir', OUTPUT_DIR
    ]
    process = subprocess.Popen(command)
    return process

def main(install_requirements_flag=True):
    # Step 1: Optionally install requirements
    base_directory = os.path.join(COMFY_DIR, 'custom_nodes')
    requirements_dirs = find_requirements_dirs(base_directory)
    
    if install_requirements_flag and requirements_dirs:
        install_requirements(requirements_dirs)
    elif install_requirements_flag:
        print("No subdirectories with requirements.txt found.")

    # Step 2: Start ComfyUI instances in separate threads
    processes = []
    with ExitStack() as stack:
        for device in CUDA_DEVICES:
            port = START_PORT + device
            print(f"Starting ComfyUI on port {port} with CUDA device {device}")
            process = run_comfyui_instance(port, device)
            processes.append(process)
            stack.callback(process.terminate)  # Ensure process terminates on exit

        # Wait for all processes to complete
        for process in processes:
            process.wait()

if __name__ == "__main__":
    main(install_requirements_flag=False)