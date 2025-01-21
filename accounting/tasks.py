from time import sleep
# from inventoryAPI.celery import celery
from celery import shared_task


# @celery.task
@shared_task
def notify_message(message):
    print("sending message")
    print(message)
    sleep(10)
    print("Sent")
