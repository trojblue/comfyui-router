# %cd /lv0/dev/comfyui-router

import os
import subprocess
import requests
from contextlib import ExitStack
from tqdm import tqdm

from .utils import get_config

COMFY_DIR = "/rmt/yada/apps/comfyui"
START_PORT = 18188
END_PORT = 18195  # Specify the end port for scanning
MQ_IP = "52.10.216.28"
BROKER_URL = f'pyamqp://runner:UjLyQtRMWTG68aAKecq4Hn@{MQ_IP}//'
CELERY_APP_NAME = 'comfyui_router.tasks'
CELERY_MODULE = 'comfyui_router.tasks'


def is_comfyui_port_active(port):
    """Check if a given port is an active ComfyUI instance with debug information."""
    url = f'http://127.0.0.1:{port}/system_stats'
    try:
        # Attempt to connect to the specified port and retrieve the system status
        response = requests.get(url, timeout=2)
        if response.status_code == 200 and 'application/json' in response.headers['Content-Type']:
            device = response.json().get('devices', {})[0]['name']
            print(f"Active ComfyUI instance detected at port {port}: {device}")
            return True
    except requests.ConnectionError as e:
        print(f"ConnectionError for {url}: {e}")
    except requests.Timeout as e:
        print(f"TimeoutError for {url}: {e}")
    except Exception as e:
        print(f"Unexpected error while connecting to {url}: {e}")
    return False

def start_celery_worker(port):
    """Start a Celery worker for a specific ComfyUI instance port."""
    command = [
        'celery', '-A', CELERY_MODULE, 'worker',
        '--loglevel=info',
        '--concurrency=1',  # Single worker per instance
        '-n', f'worker_{port}@%h'  # Unique worker name per port
    ]
    env = os.environ.copy()
    env['BROKER_URL'] = BROKER_URL
    process = subprocess.Popen(command, env=env)
    return process

def main():
    # Step 1: Scan for active ComfyUI ports
    active_ports = []
    for port in tqdm(range(START_PORT, END_PORT + 1), desc="Scanning ports"):
        if is_comfyui_port_active(port):
            active_ports.append(port)

    if not active_ports:
        print("No active ComfyUI instances found.")
        return

    # Step 2: Start a separate Celery worker for each active port
    print(f"Starting Celery workers for the following active ports: {active_ports}")
    processes = []
    with ExitStack() as stack:
        for port in active_ports:
            print(f"Starting Celery worker for port {port}...")
            process = start_celery_worker(port)
            processes.append(process)
            stack.callback(process.terminate)  # Ensure process terminates on exit

        # Wait for all processes to complete
        for process in processes:
            process.wait()

if __name__ == "__main__":
    main()