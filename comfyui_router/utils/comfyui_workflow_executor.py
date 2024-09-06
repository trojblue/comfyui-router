from typing import Dict, Any, Iterator, Tuple, List, Tuple, Callable

# NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import websocket
import uuid
import json

import urllib.request
import urllib.parse

from PIL import Image
import io

class Workflow:
    def __init__(self, raw_json: Dict[str, Any]):
        self.raw_json = raw_json
        self._modifiable_keys = self._extract_modifiable_keys()

    def _extract_modifiable_keys(self) -> Dict[str, Tuple[str, Any]]:
        """Extracts and returns a dictionary of modifiable keys and their content."""
        modifiable_keys = {}
        for node_id, node_data in self.raw_json.items():
            if node_data['class_type'] == 'TaggedAny':
                tag = node_data['inputs'].get('tag')
                content = node_data['inputs'].get('content')
                if tag and content:
                    modifiable_keys[tag] = (node_id, content)
        return modifiable_keys

    def get_modifiable_keys(self) -> Dict[str, Any]:
        """Returns a dictionary of modifiable keys and their content."""
        try:
            keys = {key: value[1]
                    for key, value in self._modifiable_keys.items()}
        except Exceptions as e:
            raise ValueError(
                f"Workflow does not contain any modifiable keys. It's not exportd as API format?\n{e} | {e.__class__.__name__}")

        return keys

    def update_modifiable_keys(self, overrides: Dict[str, Any]) -> None:
        """Updates the modifiable keys using the given overrides."""
        for key, value in overrides.items():
            if key in self._modifiable_keys:
                node_id, _ = self._modifiable_keys[key]
                self.raw_json[node_id]['inputs']['content'] = value
                self._modifiable_keys[key] = (node_id, value)

    def export(self) -> Dict[str, Any]:
        """Exports the workflow as a dictionary."""
        return self.raw_json

    def __getitem__(self, key: str) -> Any:
        """Allows direct access to raw_json like a dictionary."""
        return self.raw_json[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Allows direct setting of items in raw_json like a dictionary."""
        self.raw_json[key] = value
        self._modifiable_keys = self._extract_modifiable_keys()  # Refresh modifiable keys

    def __delitem__(self, key: str) -> None:
        """Allows direct deletion of items in raw_json like a dictionary."""
        del self.raw_json[key]
        self._modifiable_keys = self._extract_modifiable_keys()  # Refresh modifiable keys

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """Allows iteration over the raw_json as key-value pairs."""
        return iter(self.raw_json.items())

    def __len__(self) -> int:
        """Returns the length of the raw_json."""
        return len(self.raw_json)

    def __repr__(self) -> str:
        """Custom representation for the Workflow class."""
        return f"<Workflow with {len(self.raw_json)} nodes> | modifiable keys: {list(self._modifiable_keys.keys())}"


class WorkflowExecutor:
    def __init__(self, server_address="127.0.0.1:8188", timeout=120):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.timeout = timeout  # Timeout in seconds

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(
            f"http://{self.server_address}/prompt", data=data, method="POST")
        # Set timeout
        return json.loads(urllib.request.urlopen(req, timeout=self.timeout).read())

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename,
                "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}", timeout=self.timeout) as response:
            return response.read()  # Set timeout

    def get_history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}", timeout=self.timeout) as response:
            return json.loads(response.read())  # Set timeout

    def get_images(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_images = {}
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message['type'] == 'executing':
                    data = message['data']
                    if data['node'] is None and data['prompt_id'] == prompt_id:
                        break  # Execution is done
            else:
                continue  # Previews are binary data

        history = self.get_history(prompt_id)[prompt_id]
        for node_id, node_output in history['outputs'].items():
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = self.get_image(
                        image['filename'], image['subfolder'], image['type']
                    )
                    images_output.append(image_data)
                output_images[node_id] = images_output

        return output_images

    def run_workflow(self, workflow_json: dict):
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}",
                   timeout=self.timeout)  # Set timeout
        images = self.get_images(ws, workflow_json)
        return images

    def __call__(self, workflow_json: dict):
        return self.run_workflow(workflow_json)
    


def extract_images_from_response(raw_response:dict):
    """
    Extracts images from the raw response of the ComfyUI pipeline.

    Parameters:
        raw_response: The raw response from the ComfyUI pipeline

    Returns:
        {'103': [<PIL.PngImagePlugin.PngImageFile image mode=RGB size=896x1152>,
        <PIL.PngImagePlugin.PngImageFile image mode=RGB size=896x1152>]}
    """
    extracted_images = {}
    
    for node_id, result_data_list in raw_response.items():
        images = []
        for result_data in result_data_list:
            if isinstance(result_data, bytes):
                # Process binary data (e.g., image)
                try:
                    img = Image.open(io.BytesIO(result_data))
                    images.append(img)
                except Exception as e:
                    print(f"Error decoding image for node {node_id}: {e}")
            else:
                # Handle other data types if necessary, here we are only interested in images
                print(f"Non-image data encountered in node {node_id}: {result_data}")
        
        if images:
            extracted_images[node_id] = images
    
    return extracted_images