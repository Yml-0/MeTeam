from qrcode_styled import ERROR_CORRECT_Q, QRCodeStyled
from qrcode.constants import ERROR_CORRECT_L
from aiogram import Bot, Dispatcher, types
from aiogram.types.message import ContentType
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import aiogram.utils.markdown as md
from PIL import Image, ImageDraw, ImageOps
from deep_translator import GoogleTranslator

import qrcode
import os
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
    results = State()
    results2 = State()
    results3 = State()

#buttons
start_butn_user = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мероприятия')],
        # [KeyboardButton(text='Фиджитал игры')],
        # [KeyboardButton(text='Мои мероприятия')],
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

def do_pages(limit):
    events = db_fetchall('SELECT name, rowid FROM events')
    events_len = len(db_fetchall("SELECT * FROM events"))
    arr = [[]]
    if events_len % limit == 0:
        pages = events_len // limit
    else:
        pages = events_len // limit + 1
    while len(arr) < pages:
        arr.append([])
    for i in range(events_len):
        arr[i // limit].append(events[i])
    return arr

def get_page(page, limit):
    return do_pages(limit)[page - 1]

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    tg_id = message.from_user.id
    db_role = db_fetchone("SELECT role FROM users WHERE id = ?", (tg_id,))
    if db_role is not None:
        db_role = db_role[0]
    if db_role is None:
        db_execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (0, 0, 0, tg_id, 0, 0, 0))
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


@dp.message_handler(commands=["form"])
async def form(message: types.Message):
    rowid = 1
    link = "https://forms.gle/9tRb3qM92aPRhGgq9"
    text = "Добрый день всем участникам <b>Фиджитал Игр</b> в ГБОУ Школа 1547!\n\nОтветьте, пожалуйста, на <b>вопросы формы</b>, нажав на кнопку."
    form = types.InlineKeyboardMarkup(2)
    form.add(types.InlineKeyboardButton(text="Ответить", callback_data=f"chanel", url=f"{link}"))
    str_ent = db_fetchone("SELECT * FROM events WHERE rowid = ?", (rowid,))[3].split(",")
    if message.from_user.id != 639545029 or message.from_user.id != 1087465791:
        try:
            for i in range(len(str_ent)):
                await bot.send_message(int(str_ent[i]), text, parse_mode="HTML", reply_markup=form)
            await message.answer("Успех!")
        except:
            await message.answer("Возникла какая-то ошибка👀")


@dp.message_handler(commands=["results"])
async def results(message: types.Message):
    if message.from_user.id != 639545029 or message.from_user.id != 1087465791:
        await message.answer("Введите Название команды, которая заняла 1 место")
        await Form.results.set()
    else:
        await message.answer("Ты не админ!")


@dp.message_handler(state=Form.results)
async def results(message: types.Message, state: FSMContext):
    place1 = message.text
    await message.answer("Введите Название команды, которая заняла 2 место")
    await Form.results2.set()
    async with state.proxy() as data:
        data['place1'] = place1


@dp.message_handler(state=Form.results2)
async def results2(message: types.Message, state: FSMContext):
    place1 = (await state.get_data())['place1']
    place2 = message.text
    await message.answer("Введите Название команды, которая заняла 3 место")
    await Form.results3.set()
    async with state.proxy() as data:
        data['place1'] = place1
        data['place2'] = place2


@dp.message_handler(state=Form.results3)
async def results3(message: types.Message, state: FSMContext):
    rowid = 1
    place1 = (await state.get_data())['place1']
    place2 = (await state.get_data())['place2']
    place3 = message.text
    str_ent = db_fetchone("SELECT * FROM events WHERE rowid = ?", (rowid,))[3].split(",")
    text = f"Уважаемые участники <b>Фиджитал Игр!</b>\nМы подвели итоги и публикуем результаты:\n1 место – <i>{place1}</i>\n2 место – <i>{place2}</i>\n3 место – <i>{place3}</i>\nБлагодарим всех за активное участие! До новых встреч!"
    try:
        for i in range(len(str_ent)):
            await bot.send_message(int(str_ent[i]), text, parse_mode="HTML")
    except:
        await message.answer("Ошибка. Возможно, пользователей нет в базе данных")
    await message.answer("Результаты опубликованы!")
    await state.finish()


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


@dp.message_handler(text='Мероприятия')
async def events(message: types.Message):
    page = 1
    limit = 4
    arr = get_page(page, limit)
    events_len = len(db_fetchall("SELECT * FROM events"))
    event = types.InlineKeyboardMarkup(2)
    for i in arr:
        event.add(types.InlineKeyboardButton(text=i[0], callback_data=f"page|btn|{i[1]}|{page}"))
    if events_len > limit:
        list = []
        list.append(types.InlineKeyboardButton(text="»", callback_data=f"page|page|{page+1}"))
        event.add(*list)
    await message.answer("Доступные мероприятия:", reply_markup=event)


@dp.callback_query_handler(lambda c: c.data.startswith('page'))
async def page(callback: types.CallbackQuery):
    data = callback.data.split('|')
    if data[1] == "btn":
        rowid = data[2]
        page = int(data[3])
        name = db_fetchone("SELECT * FROM events WHERE rowid = ?", (rowid,))[0]
        description = db_fetchone("SELECT * FROM events WHERE rowid = ?", (rowid,))[1]
        date = db_fetchone("SELECT * FROM events WHERE rowid = ?", (rowid,))[2]
        place = db_fetchone("SELECT * FROM events WHERE rowid = ?", (rowid,))[5]
        regin = types.InlineKeyboardMarkup(2)
        regin.add(types.InlineKeyboardButton(text="Участвовать", callback_data=f"registration|{rowid}"))
        regin.add(types.InlineKeyboardButton(text="Назад", callback_data=f"page|page|{page}"))
        await callback.message.edit_text(f'Мероприятие: "{name}"\nДата проведения: {date}\nМесто проведения: {place}\n\n{description}', reply_markup=regin)
    elif data[1] == "page":
        page = int(data[2])
        limit = 4
        arr = get_page(page, limit)
        events_len = len(db_fetchall("SELECT * FROM events"))
        if events_len % limit == 0:
            pages = events_len // limit
        else:
            pages = events_len // limit + 1
        if page == pages:
            event = types.InlineKeyboardMarkup(2)
            for i in arr:
                event.add(types.InlineKeyboardButton(text=i[0], callback_data=f"page|btn|{i[1]}|{page}"))
            if events_len > limit:
                list = []
                list.append(types.InlineKeyboardButton(text="«", callback_data=f"page|page|{page-1}"))
                event.add(*list)
            await callback.message.edit_text("Доступные мероприятия:", reply_markup=event)
        elif page == 1:
            event = types.InlineKeyboardMarkup(2)
            for i in arr:
                event.add(types.InlineKeyboardButton(text=i[0], callback_data=f"page|btn|{i[1]}|{page}"))
            if events_len > limit:
                list = []
                list.append(types.InlineKeyboardButton(text="»", callback_data=f"page|page|{page+1}"))
                event.add(*list)
            await callback.message.edit_text("Доступные мероприятия:", reply_markup=event)
        else:
            event = types.InlineKeyboardMarkup(2)
            for i in arr:
                event.add(types.InlineKeyboardButton(text=i[0], callback_data=f"page|btn|{i[1]}|{page}"))
            list = []
            list.append(types.InlineKeyboardButton(text="«", callback_data=f"page|page|{page-1}"))
            list.append(types.InlineKeyboardButton(text="»", callback_data=f"page|page|{page+1}"))
            event.add(*list)
            await callback.message.edit_text("Доступные мероприятия:", reply_markup=event)


@dp.callback_query_handler(lambda c: c.data.startswith('registration'))
async def registration(callback: types.CallbackQuery):
    data = callback.data.split('|')
    rowid = data[1]
    tg_id = callback.from_user.id
    ids = db_fetchone("SELECT members_id FROM events WHERE rowid = ?", (rowid,))[0]
    if ids == None or ids == "0":
        db_execute("UPDATE events SET members_id = (?) WHERE rowid = (?)", (tg_id, rowid))
    else:
        ids = ids.split(',')
        if str(tg_id) in ids:
            await callback.message.edit_text("Вы уже зарегистрированы на это мероприятие!", reply_markup=None)
            return
        else:
            ids.append(str(tg_id))
            ids = ','.join(ids)
            db_execute("UPDATE events SET members_id = (?) WHERE rowid = (?)", (ids, rowid))

    ids_users = db_fetchone("SELECT events FROM users WHERE id = ?", (tg_id,))[0]
    if ids_users == None or ids_users == "0":
        db_execute("UPDATE users SET events = (?) WHERE id = (?)", (rowid, tg_id))
    else:
        ids_users = ids_users.split(',')
        if str(rowid) in ids_users:
            return
        else:
            ids_users.append(str(rowid))
            ids_users = ','.join(ids_users)
            db_execute("UPDATE users SET events = (?) WHERE id = (?)", (ids_users, tg_id))
    await callback.message.edit_text("Вы успешно зарегистрировались на мероприятие!", reply_markup=None) #Активные мероприятия можно посмотреть в профиле

    #creating qr
    event_name = db_fetchone("SELECT name FROM events WHERE rowid = ?", (rowid,))[0]
    name = db_fetchone("SELECT name FROM users WHERE id = ?", (tg_id,))[0]
    surname = db_fetchone("SELECT surname FROM users WHERE id = ?", (tg_id,))[0]
    second_name = db_fetchone("SELECT second_name FROM users WHERE id = ?", (tg_id,))[0]
    fio = name + " " + surname + " " + second_name
    filename = f"{tg_id}.png"
    qr = QRCodeStyled(error_correction=ERROR_CORRECT_L)
    with open(os.path.join("qr_codes/", filename), 'wb') as photo:
        qr.get_image(f"{name} {surname}").save(photo, "WEBP", quality=0)
    img1 = Image.open(os.path.join("qr_codes/background/background.png"))
    img2 = Image.open(os.path.join("qr_codes/", filename))
    img2 = img2.resize((850, 850))
    im = img2.crop((5, 5, img2.size[0]-5, img2.size[1]-5))
    img1.paste(im, (340, 735))
    img1.save(os.path.join("qr_codes/", filename))
    await bot.send_photo(tg_id, open(os.path.join("qr_codes/", filename), 'rb'), caption="Ваш QR-код для прохода на мероприятие")


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
    await message.answer(f"<i><b>ФИО</b></i> — {fio}\n\n<i><b>Роль</b></i> — {role}\n\n{balance}", parse_mode="HTML")
    #Сделать кнопку отправки заявки на получение роли организатора и мои мероприятия


@dp.message_handler(text="Назад")
async def back(message: types.Message):
    tg_id = message.from_user.id
    role = db_fetchone("SELECT role FROM users WHERE id = ?", (tg_id,))[0]
    if role == 0:
        await message.answer("Меню", reply_markup=start_butn_user)
    elif role == 1:
        await message.answer("Меню", reply_markup=start_butn_admin)


executor.start_polling(dp, skip_updates=False)