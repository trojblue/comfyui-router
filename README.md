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

## Setup project

```bash
git clone https://github.com/trojblue/comfyui-router && cd comfyui-router
pip install -e .
```



## Starting Worker

```bash
celery -A comfyui_router.tasks worker --loglevel=info
```



