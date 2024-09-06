

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