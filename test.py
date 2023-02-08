import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import ParseMode

API_TOKEN = os.environ.get('BOT_TOKEN', '')

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()

# Setup bot and dispatcher
bot = Bot("5968515856:AAEyXXUe_jz25FGJl0aoyf59JT2Jc74CiPI")
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(LifetimeControllerMiddleware())

# States
class Form(states.Form):
    number_of_buttons = states.IntegerState(default=4)

@dp.message_handler(commands='start', state=None)
@dp.message_handler(commands='help', state=None)
@dp.message_handler(lambda message: True, state=None)
async def cmd_start(message: Message):
    """
    User command handler
    """
    await Form.number_of_buttons.set()
    await message.answer("How many buttons do you want to have on each page?")

# You can use state '*' if you need to handle all states
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.number_of_buttons)
@dp.message_handler(lambda message: message.text.isdigit(), state='*')
async def process_number_of_buttons(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['number_of_buttons'] = int(message.text)

    buttons_per_page = data['number_of_buttons']

    pages = []
    for i in range(0, len(all_buttons), buttons_per_page):
        pages.append(all_buttons[i:i + buttons_per_page])

    markup = types.InlineKeyboardMarkup()
    callbacks = []
    for i, page in enumerate(pages):
        row = []
        for button in page:
            callback = f"page_{i}"
            callbacks.append(callback)
            row.append(types.InlineKeyboardButton(button, callback_data=callback))
        markup.add(*row)
        markup.add(types.InlineKeyboardButton("Next page", callback_data=f"page_{i + 1}"))

    message = await bot.send_message(
        chat_id=message.chat.id,
        text="Please choose a button.",
        reply_markup=markup,
    )

    async with state.proxy() as data:
        data["pages"] = pages
        data["current_page"] = 0
        data["message_id"] = message.message_id

    return await Form.Next()