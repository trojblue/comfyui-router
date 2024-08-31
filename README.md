# comfyui-router
Distributed task dispatcher for comfyui clusters


(WIP)

## Setup project
```bash
pip install -e .
```


## Setup RabbitMQ
> https://www.rabbitmq.com/docs/download

```bash
./setup/rabbitmq.sh
sudo systemctl status rabbitmq-server 

# ./cfed tunnel --url http://localhost:15672
# go to localhost:15672, or use tunnel to view admin panel
```


## Starting Worker

```bash
celery -A comfyui_router.tasks worker --loglevel=INFO

```