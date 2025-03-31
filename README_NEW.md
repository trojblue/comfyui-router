

## Setup:
```bash
git clone ...
cd ...
pip install -e .

# setup comfyui, celery etc
crt configure  

# then launch a comfyui normally, or use crt launch_comfy to launch multiple comfyui:
crt launch-comfy
```


## Adding to comfyui custom nodes:

```bash
cd /rmt/yada/apps/comfyui/custom_nodes/
ln -s /rmt/yada/dev/comfyui-router ./comfyui-router

```



## Minimum Usage


when at least one worker is online, use the following code to get a response:

```python
import json
import msgpack
from celery import Celery

import unibox as ub

from comfyui_router.utils import Workflow
from comfyui_router.utils import get_router_config
from comfyui_router.utils import extract_images_from_response

# Initialize Celery client to connect to the broker
broker_url = get_router_config("BROKER_URL")
app = Celery('tasks', broker=broker_url, backend='rpc://')

# Unique key for the request
unique_key = "debug_request_001"

# Send the request to the Celery worker
result = app.send_task('comfyui_router.tasks.process_request', args=[unique_key, dict(wf)])

# Wait for the result (blocking)
packed_response = result.get(timeout=40)  # You can adjust the timeout as needed

# Decode the MessagePack response
_, raw_response = msgpack.unpackb(packed_response, raw=False)

node_imgs = extract_images_from_response(raw_response)
node_imgs
```