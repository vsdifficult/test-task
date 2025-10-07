from celery import shared_task
from django.utils.timezone import now
from notifications.models import Notification
from tasks.models import Task
from django.conf import settings
from aiogram import Bot
import asyncio

async def send_message_async(telegram_id, message):
    """Asynchronously sends a message to a given Telegram ID."""
    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("Telegram bot token is not configured. Skipping notification.")
        return
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        await bot.send_message(chat_id=telegram_id, text=message)
    except Exception as e:
        print(f"Failed to send Telegram message to {telegram_id}: {e}")
    finally:
        await bot.session.close()

def send_telegram_message(telegram_id, message):
    """Synchronous wrapper to run the async message sending function."""
    if telegram_id:
        try:
            asyncio.get_running_loop()
            asyncio.ensure_future(send_message_async(telegram_id, message))
        except RuntimeError:  
            asyncio.run(send_message_async(telegram_id, message))

@shared_task
def send_due_task_notifications():
    due_tasks = Task.objects.filter(due_date__lte=now(), completed=False)
    for task in due_tasks:
        message = f"Task '{task.title}' is due!"
        Notification.objects.create(user=task.assigned_to, message=message, task=task)
        if task.assigned_to.telegram_id:
            send_telegram_message(task.assigned_to.telegram_id, message)

@shared_task
def send_task_assigned_notification(task_id):
    task = Task.objects.get(id=task_id)
    message = f"You have been assigned a new task: '{task.title}'"
    Notification.objects.create(user=task.assigned_to, message=message, task=task)
    if task.assigned_to.telegram_id:
        send_telegram_message(task.assigned_to.telegram_id, message)
