# comfyui_router/celery_app.py

from celery import Celery

app = Celery('comfyui_router', broker='pyamqp://runner:UjLyQtRMWTG68aAKecq4Hn@localhost//')

@app.task
def some_task():
    return "Task completed"
