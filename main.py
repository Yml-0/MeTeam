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
from deep_translator import GoogleTranslator

import uuid
import time
import random
import sqlite3
import copy



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
        # [KeyboardButton(text='Фиджитал игры')],
        [KeyboardButton(text='Мои мероприятия')],
        [KeyboardButton(text='Профиль')],
    ], resize_keyboard=True
)


start_butn_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мероприятия')],
        [KeyboardButton(text='Мои мероприятия')],
        [KeyboardButton(text='Профиль')],
        [KeyboardButton(text='Fiji')],
    ], resize_keyboard=True
)


eventuser = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Доступные мероприятия')],
        [KeyboardButton(text='Приватные мероприятия')],
        [KeyboardButton(text='Назад')],
    ], resize_keyboard=True
)


regfiji = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Записаться на мероприятие')],
        [KeyboardButton(text='Назад')],
    ], resize_keyboard=True
)


eventorg = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Доступные мероприятия')],
        [KeyboardButton(text='Приватные мероприятия')],
        [KeyboardButton(text='Создать мероприятие')],
        [KeyboardButton(text='Назад')],
    ], resize_keyboard=True
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

def db_getlen(table):
    return len(db_fetchall(f'SELECT * FROM {table}'))

def split_list(input_list):
    output = []
    for i in range(0, len(input_list), 5):
        output.append(input_list[i:i+5])
    return output


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
        await message.answer("Привет, я бот, который поможет тебе участвовать в мероприятиях школы и получать крутые призы!\nТакже подписывайся на нашу группу, чтобы не пропустить ни одного мероприятия!", reply_markup=chanel)
        time.sleep(2)
        markup = types.ReplyKeyboardRemove()
        await message.answer("Для начала, напиши своё <i>имя</i>, чтобы я мог тебя запомнить!", reply_markup=markup, parse_mode="HTML")
        await Form.name.set()
    elif db_role == 0:
        await message.answer("Меню", reply_markup=start_butn_user)
    elif db_role == 1:
        await message.answer("Меню", reply_markup=start_butn_admin)



@dp.message_handler(state=Form.name)
async def name(message: types.Message, state: FSMContext):
    name = message.text
    db_execute("UPDATE users SET name = (?) WHERE id = (?)", (name, message.from_user.id))
    await message.answer("Молодец! Теперь мне нужна твоя <i>фамилия</i>", parse_mode="HTML")
    await Form.sname.set()
    

@dp.message_handler(state=Form.sname)
async def sname(message: types.Message, state: FSMContext):
    surname = message.text
    db_execute("UPDATE users SET surname = (?) WHERE id = (?)", (surname, message.from_user.id))
    await message.answer("Последний шаг! Напиши своё <i>отчество</i>", parse_mode="HTML")
    await Form.sec_name.set()


@dp.message_handler(state=Form.sec_name)
async def secname(message: types.Message, state: FSMContext):
    second_name = message.text
    db_execute("UPDATE users SET second_name = (?) WHERE id = (?)", (second_name, message.from_user.id))
    await message.answer("<b>Регистрация завершена</b>✅\nИзменить <i>свои данные</i> можно в профиле!", reply_markup=start_butn_user, parse_mode="HTML")
    await state.finish()

a = {}

@dp.message_handler(text='Мероприятия')
async def games(message: types.Message):
    events = db_fetchall("SELECT name, rowid FROM events")
    arr = [[]]
    n = len(events)
    q = 4
    if n%q == 0:
        pages = n//q
    else:
        pages = n//q + 1
    while len(arr) < pages:
        arr.append([])
    for i in range(n):
        arr[i//q].append(events[i][0])
    for i in range(len(arr)):
        arr[i].append('»')
    event = types.InlineKeyboardMarkup(1)
    listall = copy.deepcopy(arr)
    arrarch = copy.deepcopy(arr)
    listall1 = ""
    arrarch1 = ""
    listall.remove(listall[0])
    for i in listall:
        for j in i:
            listall1 += f"{j},"
    for k in arrarch:
        for x in k:
            arrarch1 += f"{x},"
    print(len(arrarch1))
    for i in arr[0]:
        event.add(types.InlineKeyboardButton(text=i, callback_data=f"page|{i}|{listall1}"))
    await message.answer("Мероприятия", reply_markup=event)
#функция, которая принимает кол-во элементов на странице и страницу и возвращает маленький массив из событий
#поставить фильтр по id >= N и limit 5
#для самого первого запроса не нужно ставить фильтр по id и ставить просто limit 5
#если полетит сервер, то исчезнет бд, поэтому стоит задуматься над облачными серверами

@dp.callback_query_handler(lambda c: c.data.startswith('page'))
async def page(callback: types.CallbackQuery):
    data = callback.data.split('|')
    if data[1] == '»':
        a = data[2].split(', ')
        a.remove(a[-1])
        print(split_list(a))
    else:
        await bot.edit_message_reply_markup(callback.from_user.id, callback.message.message_id, reply_markup=None)



@dp.message_handler(text="Профиль")
async def profile(message: types.Message):
    tg_id = message.from_user.id
    name = db_fetchone("SELECT name FROM users WHERE id = ?", (tg_id,))[0]
    surname = db_fetchone("SELECT surname FROM users WHERE id = ?", (tg_id,))[0]
    second_name = db_fetchone("SELECT second_name FROM users WHERE id = ?", (tg_id,))[0]
    role = db_fetchone("SELECT role FROM users WHERE id = ?", (tg_id,))[0]
    balancecoin = db_fetchone("SELECT balance FROM users WHERE id = ?", (tg_id,))[0]
    fio = f"{surname} {name} {second_name}"
    if role == 0:
        role = "Пользователь"
    elif role == 1:
        role = "Организатор"
    elif role == 2:
        role = "Администратор"
    if balancecoin == 1:
        translate = f'1 fidjicoin'
        translated = GoogleTranslator(source='en', target='ru').translate(translate)
    else:
        translate = f'{balancecoin} fidjicoins'
        translated = GoogleTranslator(source='en', target='ru').translate(translate)
    balance = f"<i><b>Баланс</b></i> — {translated}"
    await message.answer(f"<i><b>ФИО</b></i> — {fio}\n\n<i><b>Роль</b></i> — {role}\n\n{balance}", parse_mode="HTML")  #reply_markup=start_butn

# @dp.message_handler(text="Мероприятия")
# async def events(message: types.Message):
#     tg_id = message.from_user.id
#     role = db_fetchone("SELECT role FROM users WHERE id = ?", (tg_id,))[0]
#     if role == 0:
#         msg = await message.answer("Панель мероприятий", reply_markup=eventuser)
#     elif role == 1:
#         msg = await message.answer("Панель мероприятий", reply_markup=eventorg)


@dp.message_handler(text="Назад")
async def back(message: types.Message):
    tg_id = message.from_user.id
    role = db_fetchone("SELECT role FROM users WHERE id = ?", (tg_id,))[0]
    if role == 0:
        await message.answer("Меню", reply_markup=start_butn_user)
    elif role == 1:
        await message.answer("Меню", reply_markup=start_butn_admin)


executor.start_polling(dp, skip_updates=False)