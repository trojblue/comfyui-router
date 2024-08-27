from PIL import Image

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