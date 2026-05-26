from celery import Celery

celery = Celery(
    "crm_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery.conf.task_routes = {
    "tasks.process_message_task": {"queue": "crm_queue"},
}
