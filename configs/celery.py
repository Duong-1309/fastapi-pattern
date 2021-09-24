from celery import Celery
from configs.settings import CELERY_APP_NAME



app_celery = Celery(
    f'{CELERY_APP_NAME}',
    broker='amqps://clzxtneg:A3_uOi1WMhFPKXnCi7WTUeLq8shklii4@snake.rmq2.cloudamqp.com/clzxtneg',
    include=['app.tasks']
)

app_celery.config_from_object('configs.celeryconfig')
app_celery.autodiscover_tasks()
