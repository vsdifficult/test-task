import asyncio
import os
import django
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()

from django.conf import settings
from accounts.models import CustomUser
from tasks.models import Task
from asgiref.sync import sync_to_async

logging.basicConfig(level=logging.INFO)

if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    raise ValueError("Telegram bot token is not configured in Django settings.")

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@sync_to_async
def get_user_by_telegram_id(telegram_id):
    try:
        return CustomUser.objects.get(telegram_id=str(telegram_id))
    except CustomUser.DoesNotExist:
        return None

@dp.message(CommandStart())
async def send_welcome(message: Message):
    """Handler for /start command."""
    user = await get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.reply(
            f"Hello, {user.username}! Your account is already linked.\n"
            f"You can view your tasks with the /tasks command."
        )
    else:
        # In a real-world scenario, you'd generate a unique, short-lived token.
        # For this task, we'll use the user's Telegram ID as a simple linking token.
        await message.reply(
            f"Hello! To link your account, please go to your profile on the website "
            f"and enter the following code in the 'Link Telegram' section:\n\n"
            f"`{message.from_user.id}`\n\n"
            f"After linking, use the /tasks command to see your tasks.",
            parse_mode="Markdown"
        )

@dp.message(Command('tasks'))
async def show_tasks(message: Message):
    """Handler for /tasks command."""
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.reply("Your Telegram account is not linked. Please use the /start command first.")
        return

    tasks = await sync_to_async(list)(Task.objects.filter(assigned_to=user, completed=False))
    
    if not tasks:
        await message.reply("You have no pending tasks.")
        return

    response = "Your pending tasks:\n\n"
    for task in tasks:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Mark as Complete", callback_data=f"complete_task_{task.id}")]
        ])
        await message.answer(f"- *{task.title}*", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data.startswith('complete_task_'))
async def process_complete_task(callback_query: CallbackQuery):
    task_id = int(callback_query.data.split('_')[-1])
    user = await get_user_by_telegram_id(callback_query.from_user.id)

    try:
        task = await sync_to_async(Task.objects.get)(id=task_id, assigned_to=user)
        if not task.completed:
            task.completed = True
            await sync_to_async(task.save)()
            await callback_query.message.edit_text(f"~{task.title}~ - Completed!", parse_mode="Markdown")
        else:
            await callback_query.message.edit_text(f"{task.title} - (Already completed)")
        
        await callback_query.answer("Task marked as complete!")
    except Task.DoesNotExist:
        await callback_query.answer("Task not found or you don't have permission.")
    except Exception as e:
        logging.error(f"Error completing task: {e}")
        await callback_query.answer("An error occurred.")

async def main():
    """Starts the bot."""
    print("Starting bot...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
