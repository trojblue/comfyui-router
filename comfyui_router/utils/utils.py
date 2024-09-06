from PIL import Image
import io
import inspect
import os

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)


def _async_save(img, path, quality=95):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    executor.submit(lambda: img.save(path, quality=quality))