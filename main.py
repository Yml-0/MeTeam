from qrcode_styled import ERROR_CORRECT_Q, QRCodeStyled
from aiogram import Bot, Dispatcher, types
from aiogram.types.message import ContentType
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from PIL import Image, ImageDraw
import uuid
import time
import random


class Form(StatesGroup):
    Sname = State()


start_butn = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='.'), KeyboardButton(text='.')],
        [KeyboardButton(text='.'), KeyboardButton(text='.')],
        [KeyboardButton(text='.'), KeyboardButton(text='.')],
    ], resize_keyboard=True
)


bot = Bot(token="5968515856:AAEyXXUe_jz25FGJl0aoyf59JT2Jc74CiPI")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    chanel = types.InlineKeyboardMarkup(1)
    chanel.add(types.InlineKeyboardButton(text="ЖМИ", callback_data=f"chanel", url="https://t.me/Подписывайся_на_канал_@project_02"))
    await message.answer("Привет, я бот, который поможет тебе учавствовать в разных мероприятиях школы и получать крутые призы!\nТакже подписывайся на канал, чтобы не пропустить ни одного мероприятия!", reply_markup=chanel)
    time.sleep(2)
    await message.answer("Для начала, напиши своё имя и фамилию, чтобы я мог тебя запомнить!")
    # await Form.Sname.set()


@dp.message_handler(text = ".")
async def text(message: types.Message):
    markup = types.ReplyKeyboardRemove()
    await message.answer("Введите кол-во кнопок", reply_markup=markup)
    await Form.Sname.set()
    # uu_id = uuid.uuid4()
    # filename = f"{uu_id}.png"
    # qr = QRCodeStyled()
    # with open(f'D:/project_02/qrcodes/{filename}', 'wb') as _fh:
    #     qr.get_image(f'{uu_id}').save(_fh, 'WEBP', lossless=False, quaility=0, method=0)
    # await message.answer_photo(photo=open(f'D:/project_02/qrcodes/{filename}', "rb"))

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

@dp.message_handler(state=Form.Sname)
async def Sname(message: types.Message, state: FSMContext):
    try:
        buttons = types.InlineKeyboardMarkup(2)
        count = message.text
        list = []
        cntlist = int(count)//6
        c = ""
        for i in range(int(count)):
            list.append(types.InlineKeyboardButton(text=f"{i+1}", callback_data=f"{i}"))
        buttons.add(*list)
        await message.answer("Вот твои кнопки", reply_markup=buttons)
        await state.finish()
    except:
        await message.answer("Введите число!")
        await Form.Sname.set()

executor.start_polling(dp, skip_updates=False)