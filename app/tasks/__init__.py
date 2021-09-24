from configs.celery import app_celery
from celery.schedules import crontab
import datetime
from celery.signals import task_sent


def task_sent_handler(sender=None, task_id=None, task=None, args=None,
                      kwargs=None, **kwds):
    print("Got signal task_sent for task id %s" % (task_id, ))


task_sent.connect(task_sent_handler, sender="tasks.add")

@app_celery.task
def config_beat(crontab: crontab, data):
    app_celery.add_periodic_task(crontab, say(data), name='test add task')
    # app_celery.conf.update(beat_schedule = {
    #     'add-every-30-seconds': {
    #         'task': task,
    #         'schedule': crontab,
    #         'args': (data,)
    #     },
    # })
    return True


@app_celery.task
def add(x, y):
    return x + y


# @app_celery.au.connect
# def hello(sender, **kwargs):
#     sender.add_periodic_task(
#         10.0,
#         say.s('Hello'),
#     )

@app_celery.task
def say(arg):
    print(arg)




