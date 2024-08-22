from celery import Celery, group

app = Celery('tasks', broker='pyamqp://runner:hnj8WMEB$A5@;SRg*(YC?t@52.10.216.28/myvhost')


def process_request(json_data):
    print(json_data)
    return json_data


@app.task
def process_request(unique_key, json_data):
    # Code to process the request with ComfyUI
    # Implement your logic to send the request and get the result.
    # For example, this could send the request to the appropriate ComfyUI endpoint.
    result = some_comfyui_processing_function(json_data)  # Placeholder for actual processing
    return unique_key, result

def submit_batch(batch):
    """
    Submits a batch of tasks to the Celery queue and waits for the results.
    
    :param batch: List of tuples, each containing (unique_key, json_data)
    :return: List of tuples, each containing (unique_key, result)
    """
    tasks = [process_request.s(unique_key, json_data) for unique_key, json_data in batch]
    
    # Group the tasks and run them in parallel
    results = group(tasks).apply_async()
    
    # Wait for all results to finish and gather them
    return results.get()

# Example usage:
batch = [
    ("key1", {"param1": "value1"}),
    ("key2", {"param2": "value2"}),
    # Add more (unique_key, json_data) pairs
]

results = submit_batch(batch)

for unique_key, result in results:
    print(f"Unique Key: {unique_key}, Result: {result}")
