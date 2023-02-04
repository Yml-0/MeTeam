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
import sqlite3



bot = Bot(token="5968515856:AAEyXXUe_jz25FGJl0aoyf59JT2Jc74CiPI")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    name = State()
    sname = State()
    sec_name = State()

#buttons
start_butn_user = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мероприятия')],
        [KeyboardButton(text='Мои мероприятия')],
        [KeyboardButton(text='Профиль')],
    ], resize_keyboard=True, one_time_keyboard=True
)


start_butn_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мероприятия')],
        [KeyboardButton(text='Мои мероприятия')],
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Fiji')],
    ], resize_keyboard=True, one_time_keyboard=True
)


eventuser = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Доступные мероприятия')],
        [KeyboardButton(text='Приватные мероприятия')],
    ], resize_keyboard=True, one_time_keyboard=True
)


eventorg = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Доступные мероприятия')],
        [KeyboardButton(text='Приватные мероприятия')],
        [KeyboardButton(text='Создать мероприятие')],
    ], resize_keyboard=True, one_time_keyboard=True
)

#--------------------------------------------

def db_execute(*args, **kwargs):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(*args, **kwargs)
    db.commit()
    db.close()


def db_fetchone(*args, **kwargs):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(*args, **kwargs)
    items = cursor.fetchone()
    db.commit()
    db.close()
    return items


def db_fetchall(*args, **kwargs):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(*args, **kwargs)
    items = cursor.fetchall()
    db.commit()
    db.close()
    return items


def db_fetchmany(many, *args, **kwargs):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute(*args, **kwargs)
    items = cursor.fetchmany(many)
    db.commit()
    db.close()
    return items


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    tg_id = message.from_user.id
    db_role = db_fetchone("SELECT role FROM users WHERE id = ?", (tg_id,))
    if db_role is not None:
        db_role = db_role[0]
    if db_role is None:
        db_execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                        (0, 0, 0, tg_id, 0, 0))
        chanel = types.InlineKeyboardMarkup(1)
        chanel.add(types.InlineKeyboardButton(text="ЖМИ", callback_data=f"chanel", url="https://t.me/fidjital1547"))
        await message.answer("Привет, я бот, который поможет тебе учавствовать в разных мероприятиях школы и получать крутые призы!\nТакже подписывайся на канал, чтобы не пропустить ни одного мероприятия!", reply_markup=chanel)
        time.sleep(2)
        markup = types.ReplyKeyboardRemove()
        await message.answer("Для начала, напиши своё <i>ИМЯ</i>, чтобы я мог тебя запомнить!", reply_markup=markup, parse_mode="HTML")
        await Form.name.set()
    elif db_role == 0:
        await message.answer("Меню", reply_markup=start_butn_user)
    elif db_role == 1:
        await message.answer("Меню", reply_markup=start_butn_admin)



@dp.message_handler(state=Form.name)
async def name(message: types.Message, state: FSMContext):
    name = message.text
    db_execute("UPDATE users SET name = (?) WHERE id = (?)", (name, message.from_user.id))
    await message.answer("Молодец! 👀\nНапиши свою <i>ФАМИЛИЮ</i>", parse_mode="HTML")
    await Form.sname.set()
    

@dp.message_handler(state=Form.sname)
async def sname(message: types.Message, state: FSMContext):
    surname = message.text
    db_execute("UPDATE users SET surname = (?) WHERE id = (?)", (surname, message.from_user.id))
    await message.answer("Последний шаг! Напиши своё <i>ОТЧЕСТВО</i>", parse_mode="HTML")
    await Form.sec_name.set()


@dp.message_handler(state=Form.sec_name)
async def secname(message: types.Message, state: FSMContext):
    second_name = message.text
    db_execute("UPDATE users SET second_name = (?) WHERE id = (?)", (second_name, message.from_user.id))
    await message.answer("<b>Регистрация завершена</b>✅\nИзменить <i>свои данные</i> можно в профиле!", reply_markup=start_butn_user, parse_mode="HTML")
    await state.finish()


@dp.message_handler(text="Профиль")
async def profile(message: types.Message):
    tg_id = message.from_user.id
    name = db_fetchone("SELECT name FROM users WHERE id = ?", (tg_id,))[0]
    surname = db_fetchone("SELECT surname FROM users WHERE id = ?", (tg_id,))[0]
    second_name = db_fetchone("SELECT second_name FROM users WHERE id = ?", (tg_id,))[0]
    role = db_fetchone("SELECT role FROM users WHERE id = ?", (tg_id,))[0]
    balance = db_fetchone("SELECT balance FROM users WHERE id = ?", (tg_id,))[0]
    fio = f"{surname} {name} {second_name}"
    if role == 0:
        role = "Пользователь"
    elif role == 1:
        role = "Организатор"
    elif role == 2:
        role = "Администратор"
    await message.answer(f"<i>ФИО</i> — <b>{fio}</b>\n\n<i>Роль</i> — <b>{role}</b>\n\n<i>Баланс</i> — <b>{balance} (FijiCoins)</>", parse_mode="HTML")  #reply_markup=start_butn





executor.start_polling(dp, skip_updates=False)