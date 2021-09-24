import urllib.parse


result_backend = f'mongodb://root:rootghouldb2021@0.0.0.0:47017/?authMechanism=SCRAM-SHA-256'
result_persistent = True
mongodb_backend_settings = {
    'database': 'schedule',
    'taskmeta_collection': 'schedule_taskmeta',
}
task_reject_on_worker_lost = True
timezone = 'Asia/Ho_Chi_Minh'