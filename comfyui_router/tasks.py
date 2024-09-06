import msgpack
from celery import Celery
import json
import urllib.request
import websocket
import uuid


"""
celery -A comfyui_router.tasks worker --loglevel=info

"""

MQ_IP = "52.10.216.28"

# Initialize the Celery app
app = Celery('tasks', broker=f'pyamqp://runner:UjLyQtRMWTG68aAKecq4Hn@{MQ_IP}//', backend='rpc://')

app.conf.update(
    task_send_sent_event=False,
    task_store_errors_even_if_ignored=False,
)


class WorkflowExecutor2:
    def __init__(self, server_address="127.0.0.1:18195"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    def queue_prompt(self, prompt):
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"http://{self.server_address}/prompt", data=data, method="POST")
        return json.loads(urllib.request.urlopen(req).read())

    def get_data(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())

    def get_results(self, ws, prompt):
        prompt_id = self.queue_prompt(prompt)['prompt_id']
        output_results = {}
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
            output_data = []
            for key, value in node_output.items():
                if isinstance(value, list):  # Typically, the values might be lists
                    for item in value:
                        if isinstance(item, dict) and 'filename' in item and 'subfolder' in item and 'type' in item:
                            # Retrieve the raw binary data
                            result_data = self.get_data(item['filename'], item['subfolder'], item['type'])
                            output_data.append(result_data)
                        else:
                            # Handle other types of outputs if needed
                            output_data.append(value)
            output_results[node_id] = output_data

        return output_results

    def run_workflow(self, workflow_json: dict):
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")
        results = self.get_results(ws, workflow_json)
        return results

from comfyui_router.utils.comfyui_workflow_executor import WorkflowExecutor


@app.task
def process_request(unique_key, json_data):
    
    # PORT = 18195
    PORT = 8188

    # Initialize the WorkflowExecutor
    executor = WorkflowExecutor(server_address=f"127.0.0.1:{PORT}")

    # Run the workflow using the provided JSON data
    workflow_result = executor.run_workflow(json_data)
    print("get result")

    # Encode the entire response using MessagePack
    packed_result = msgpack.packb((unique_key, workflow_result), use_bin_type=True)

    # Return the MessagePack encoded result
    return packed_result
