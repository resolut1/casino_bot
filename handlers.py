from main import bot, dp, sql, db
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.inline_keyboard import InlineKeyboardButton
from asyncio import sleep
from typing import Union
import math
import random


async def output_database():
    for value in sql.execute("SELECT * FROM users"):
        print(value)


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await check_user_base_data(message)
    sql.execute(f"SELECT balance FROM users WHERE user_id = {message.from_user.id}")
    balance = sql.fetchone()
    balance_key = KeyboardButton(f"Твой баланс: {balance[0]} ₽")
    keyboard_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(balance_key)
    await bot.send_message(message.from_user.id, f"Вывожу твой баланс...", parse_mode="HTML",
                           reply_markup=keyboard_balance)
    await sleep(1)
    await list_game(message)


async def get_balance(message: Message):
    sql.execute(f"SELECT balance FROM users WHERE user_id = {message.from_user.id}")
    balance = sql.fetchone()
    balance_key = KeyboardButton(f"Твой баланс: {balance[0]} ₽")
    keyboard_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(balance_key)
    await bot.send_message(message.from_user.id, f"У тебя снова есть <b>5000 ₽</b>", parse_mode="HTML",
                           reply_markup=keyboard_balance)
    await sleep(1)
    await list_game(message)


@dp.message_handler(commands=['menu_game'])
async def menu_game(message: Message):
    await list_game(message)


@dp.message_handler(commands=['reset_balance'])
async def menu_game(message: Message):
    sql.execute(f"UPDATE users SET balance = {5000} WHERE user_id = {message.from_user.id}")
    db.commit()
    await get_balance(message)


@dp.message_handler(commands=['stat'])
async def menu_game(message: Message):
    sql.execute("SELECT username,balance FROM users ORDER BY balance DESC")
    count = 1
    for value in sql.fetchall():
        if count == 1:
            await bot.send_message(message.chat.id, f"{count}| {value[0]} | Баланс: {value[1]} ₽  👑")
            print(f"{count} | {value[0]} | {value[1]}")
        else:
            await bot.send_message(message.chat.id, f"{count}| {value[0]} | Баланс: {value[1]}₽ ")
            print(f"{count} | {value[0]} | {value[1]}")
        count += 1


@dp.message_handler(commands=['rules'])
async def rules(message: Message):
    await bot.send_message(message.from_user.id, "1. Кости - Если у тебя выпало больше чем у бота - ты выиграл ставку"
                                                 ", если у вас равное количетсво сыграет x2 ставка\n"
                                                 "2. Дартс - Ближе к центру и приз больше.\n"
                                                 "3. Двери - У тебя будет выбор из 3 дверей(кнопок) "
                                                 "если угадаешь получишь приз!.\n"
                                                 "4. Однорукий бандит - Одна попытка за 120 рублей, "
                                                 "Джекпот - 3500 рублей")


async def list_game(message: Union[Message, CallbackQuery]):
    dice = InlineKeyboardButton('Игра "Кости" 🎲', callback_data="kosti")
    darts = InlineKeyboardButton('Игра "Дартс" 🎯', callback_data="darts")
    bandit = InlineKeyboardButton('Игра "Однорукий бандит" 🎰', callback_data="bandit")
    door = InlineKeyboardButton('Игра "3 Двери" 🚪', callback_data="door")
    keyboard_game = InlineKeyboardMarkup()
    keyboard_game.row(dice, darts)
    keyboard_game.row(bandit)
    keyboard_game.row(door)
    await bot.send_message(message.from_user.id, "Выбирай игру и выигрывай 💵!", reply_markup=keyboard_game)


async def check_user_base_data(message: Message):
    sql.execute(f"SELECT user_id FROM users WHERE user_id = {message.from_user.id}")
    if sql.fetchone() is None:
        await bot.send_message(message.from_user.id, f"Здравствуй @{message.from_user.username}, всегда рады видеть "
                                                     f"нового пользователя 😊\nУ тебя будет начальный "
                                                     "баланс в размере <b>5000 рублей</b>, удачи)")
        sql.execute(f"INSERT INTO users VALUES ('{message.from_user.username}', {message.from_user.id}, {5000}, 'None',{0},{0}, 'None')")
        db.commit()
    else:
        await bot.send_message(message.from_user.id, f"Здравствуй @{message.from_user.username}, рады тебя снова "
                                                     f"видеть, синхронизирую твои данные ⏱")


@dp.callback_query_handler(lambda c: c.data == 'kosti')
async def kosti(call: CallbackQuery):
    sql.execute(f"UPDATE users SET status_game = 'kosti' WHERE user_id = {call.from_user.id}")
    db.commit()
    await bot.answer_callback_query(call.id, 'Удачи')
    await list_bet(call)


@dp.callback_query_handler(lambda c: c.data == 'darts')
async def darts(call: CallbackQuery):
    sql.execute(f"UPDATE users SET status_game = 'darts' WHERE user_id = {call.from_user.id}")
    db.commit()
    await bot.answer_callback_query(call.id, 'Удачи')
    await list_bet(call)


@dp.callback_query_handler(lambda c: c.data == 'door')
async def door(call: CallbackQuery):
    sql.execute(f"UPDATE users SET status_game = 'door' WHERE user_id = {call.from_user.id}")
    db.commit()
    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    balance = sql.fetchone()
    await bot.answer_callback_query(call.id, 'Удачи')
    bet1 = InlineKeyboardButton("500 ₽", callback_data='d500')
    bet2 = InlineKeyboardButton("1000 ₽", callback_data='d1000')
    keyboard_bet = InlineKeyboardMarkup().add(bet1, bet2)
    await bot.send_message(call.from_user.id, f"🚪 Выбирай ставку | Твой баланс: <b>{balance[0]} ₽</b>",
                           reply_markup=keyboard_bet)


@dp.callback_query_handler(lambda c: c.data == 'bandit')
async def bandit(call: CallbackQuery):
    sql.execute(f"UPDATE users SET status_game = 'bandit' WHERE user_id = {call.from_user.id}")
    db.commit()
    bet1 = InlineKeyboardButton("120 за попытку!", callback_data='b120')
    keyboard_bet = InlineKeyboardMarkup().add(bet1)
    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    balance = sql.fetchone()[0]
    await bot.answer_callback_query(call.id, 'Удачи')
    await call.message.answer(f"🎰. Попробуем?. Ваш баланс {balance}", reply_markup=keyboard_bet)


async def list_bet(message: Union[Message, CallbackQuery]):
    sql.execute(f"SELECT balance FROM users WHERE user_id = {message.from_user.id}")
    balance = sql.fetchone()
    bet1 = InlineKeyboardButton(f'{math.floor(balance[0]*0.05)} ₽', callback_data="bet1")
    bet2 = InlineKeyboardButton(f'{math.floor(balance[0]*0.1)} ₽', callback_data="bet2")
    bet3 = InlineKeyboardButton(f'{math.floor(balance[0]*0.2)} ₽', callback_data="bet3")
    bet4 = InlineKeyboardButton(f'{math.floor(balance[0]*1)} ₽', callback_data="bet4")
    keyboard_game = InlineKeyboardMarkup().add(bet1, bet2, bet3, bet4)
    await bot.send_message(message.from_user.id, f"Выбирай ставку | Твой баланс: <b>{balance[0]} ₽</b>",
                           reply_markup=keyboard_game)


@dp.callback_query_handler(lambda c: c.data == 'bet1')
async def bet_1(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await game_bet(call, 0.05, 'bet1')


@dp.callback_query_handler(lambda c: c.data == 'bet2')
async def bet_2(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await game_bet(call, 0.1, 'bet2')


@dp.callback_query_handler(lambda c: c.data == 'bet3')
async def bet_3(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await game_bet(call, 0.2, 'bet3')


@dp.callback_query_handler(lambda c: c.data == 'bet4')
async def bet_4(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await game_bet(call, 1, 'bet4')


@dp.callback_query_handler(lambda c: c.data == 'd500')
async def d500(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await game_door(call, 500, 'd500')


@dp.callback_query_handler(lambda c: c.data == 'd1000')
async def d1000(call: CallbackQuery):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await game_door(call, 1000, 'd1000')


async def game_door(call: CallbackQuery, bets, bet_caption):
    sql.execute(f"UPDATE users SET bet = {bets} WHERE user_id = {call.from_user.id}")
    db.commit()
    sql.execute(f"UPDATE users SET bet_caption = '{bet_caption}' WHERE user_id = {call.from_user.id}")
    db.commit()
    sql.execute(f"SELECT status_game FROM users WHERE user_id = {call.from_user.id}")
    if sql.fetchone()[0] == "door":
        price_door = random.randint(1, 3)
        sql.execute(f"UPDATE users SET rand_door = {price_door} WHERE user_id = {call.from_user.id}")
        db.commit()
        if price_door == 1:
            door1 = InlineKeyboardButton(" 🚪 ", callback_data="price")
            door2 = InlineKeyboardButton(" 🚪 ", callback_data="two")
            door3 = InlineKeyboardButton(" 🚪 ", callback_data="three")
        if price_door == 2:
            door1 = InlineKeyboardButton(" 🚪 ", callback_data="one")
            door2 = InlineKeyboardButton(" 🚪 ", callback_data="price")
            door3 = InlineKeyboardButton(" 🚪 ", callback_data="three")
        if price_door == 3:
            door1 = InlineKeyboardButton(" 🚪 ", callback_data="one")
            door2 = InlineKeyboardButton(" 🚪 ", callback_data="two")
            door3 = InlineKeyboardButton(" 🚪 ", callback_data="price")

        keyboard_door = InlineKeyboardMarkup().add(door1, door2, door3)
        await bot.send_message(call.from_user.id, f"За какой дверью приз?", reply_markup=keyboard_door)


@dp.callback_query_handler(lambda c: c.data == 'price')
async def price(call: CallbackQuery):
    sql.execute(f"SELECT rand_door FROM users WHERE user_id = {call.from_user.id}")
    price_door = sql.fetchone()[0]
    if price_door == 1:
        door1 = InlineKeyboardButton(" 💰 ", callback_data="#")
        door2 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door3 = InlineKeyboardButton(" ❌ ", callback_data="#")
    if price_door == 2:
        door1 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door2 = InlineKeyboardButton(" 💰 ", callback_data="#")
        door3 = InlineKeyboardButton(" ❌ ", callback_data="#")
    if price_door == 3:
        door1 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door2 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door3 = InlineKeyboardButton(" 💰 ", callback_data="#")
    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    balance = sql.fetchone()[0]
    sql.execute(f"SELECT bet FROM users WHERE user_id = {call.from_user.id}")
    bet = sql.fetchone()[0]
    balance = balance + (math.floor(bet * 2))
    sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
    db.commit()
    keyboard_door = InlineKeyboardMarkup().add(door1, door2, door3)
    button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
    keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
    await bot.send_message(call.from_user.id, f"Баланс {balance}", reply_markup= keyboard_for_balance)
    await bot.edit_message_text(f"Поздравляю, вы выиграли!", call.message.chat.id, message_id=call.message.message_id)
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard_door)

    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    balance = sql.fetchone()[0]
    sql.execute(f"SELECT bet_caption FROM users WHERE user_id = {call.from_user.id}")
    bet_caption = sql.fetchone()[0]
    await bot.answer_callback_query(call.id, f'Ваш текущий баланс {balance} ₽')
    one = InlineKeyboardButton("Играем!", callback_data=bet_caption)
    two = InlineKeyboardButton("Другая ставка!", callback_data='door')
    three = InlineKeyboardButton("Другая игра", callback_data='other_game')
    keyboard_choice = InlineKeyboardMarkup().add(one, two)
    keyboard_choice.row(three)
    await call.message.answer("Играем ещё в 🚪 на ставку " + str(math.floor(bet)) + ' ₽ ?',
                              reply_markup=keyboard_choice)


@dp.callback_query_handler(lambda c: c.data == 'one' or c.data == 'two' or c.data == 'three')
async def one(call: CallbackQuery):
    sql.execute(f"SELECT rand_door FROM users WHERE user_id = {call.from_user.id}")
    price_door = sql.fetchone()[0]
    if price_door == 1:
        door1 = InlineKeyboardButton(" 💰 ", callback_data="#")
        door2 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door3 = InlineKeyboardButton(" ❌ ", callback_data="#")
    if price_door == 2:
        door1 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door2 = InlineKeyboardButton(" 💰 ", callback_data="#")
        door3 = InlineKeyboardButton(" ❌ ", callback_data="#")
    if price_door == 3:
        door1 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door2 = InlineKeyboardButton(" ❌ ", callback_data="#")
        door3 = InlineKeyboardButton(" 💰 ", callback_data="#")
    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    balance = sql.fetchone()[0]
    sql.execute(f"SELECT bet FROM users WHERE user_id = {call.from_user.id}")
    bet = sql.fetchone()[0]
    balance = balance - bet
    sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
    db.commit()
    keyboard_door = InlineKeyboardMarkup().add(door1, door2, door3)
    button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
    keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
    await bot.send_message(call.from_user.id, f"Баланс {balance}", reply_markup=keyboard_for_balance)
    await bot.edit_message_text(f"Вы проиграли!", call.message.chat.id, message_id=call.message.message_id)
    await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id, reply_markup=keyboard_door)

    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    balance = sql.fetchone()[0]
    sql.execute(f"SELECT bet_caption FROM users WHERE user_id = {call.from_user.id}")
    bet_caption = sql.fetchone()[0]
    await bot.answer_callback_query(call.id, f'Ваш текущий баланс {balance} ₽')
    one = InlineKeyboardButton("Играем!", callback_data=bet_caption)
    two = InlineKeyboardButton("Другая ставка!", callback_data='door')
    three = InlineKeyboardButton("Другая игра", callback_data='other_game')
    keyboard_choice = InlineKeyboardMarkup().add(one, two)
    keyboard_choice.row(three)
    await call.message.answer("Играем ещё в 🚪 на ставку " + str(math.floor(bet)) + ' ₽ ?',
                              reply_markup=keyboard_choice)


async def game_bet(call: CallbackQuery, bets, bet_caption):
    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    sql.execute(f"UPDATE users SET bet = {math.floor(sql.fetchone()[0]*bets)} WHERE user_id = {call.from_user.id}")
    db.commit()
    sql.execute(f"SELECT status_game FROM users WHERE user_id = {call.from_user.id}")
    if sql.fetchone()[0] == "kosti":
        await sleep(0.5)
        await call.message.answer("Кубик бота")
        bot_value = await bot.send_dice(call.from_user.id, emoji="🎲")
        bot_value = bot_value['dice']['value']
        await sleep(4)
        await call.message.answer("Ваш кубик")
        user_value = await bot.send_dice(call.from_user.id, emoji="🎲")
        user_value = user_value['dice']['value']
        await sleep(4)
        if user_value > bot_value:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance += math.floor(balance * bets)
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Вы победили!", reply_markup=keyboard_for_balance)
        elif user_value < bot_value:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance -= math.floor(balance * bets)
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Вы проиграли!", reply_markup=keyboard_for_balance)
        else:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance += math.floor(balance * bets)*2
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Ух ты... сыграла ставка x2", reply_markup=keyboard_for_balance)

        sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
        balance = sql.fetchone()[0]
        await bot.answer_callback_query(call.id, f'Ваш текущий баланс {balance} ₽')
        one = InlineKeyboardButton("Играем!", callback_data=bet_caption)
        two = InlineKeyboardButton("Другая ставка!", callback_data='kosti')
        three = InlineKeyboardButton("Другая игра", callback_data='other_game')
        keyboard_choice = InlineKeyboardMarkup().add(one, two)
        keyboard_choice.row(three)
        await call.message.answer("Играем ещё в 🎲 на ставку " + str(math.floor(balance*bets)) + ' ₽ ?',
                                  reply_markup=keyboard_choice)

    sql.execute(f"SELECT status_game FROM users WHERE user_id = {call.from_user.id}")
    if sql.fetchone()[0] == "darts":
        await sleep(0.5)
        await call.message.answer("Бросаем...")
        user_value = await bot.send_dice(call.from_user.id, emoji="🎯")
        user_value = user_value['dice']['value']
        await sleep(3.5)
        if user_value == 1:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance -= math.floor(balance * bets)
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Никуда не годится", reply_markup=keyboard_for_balance)
        if user_value == 2:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance = balance - math.floor(balance*bets) + math.floor((balance*bets)*0.1)
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("На грани, возвращаем только 10% от ставки", reply_markup=keyboard_for_balance)
        if user_value == 3:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance = balance - math.floor(balance*bets) + math.floor((balance*bets)*0.2)
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("На грани, возвращаем только 20% от ставки", reply_markup=keyboard_for_balance)
        if user_value == 4:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance = balance+500
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Неплохо. Бонус! + 150 ₽", reply_markup=keyboard_for_balance)
        if user_value == 5:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance += math.floor(balance * bets)
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Отлично", reply_markup=keyboard_for_balance)
        if user_value == 6:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance += math.floor(balance * bets) * 2
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Сыграла ставка x2", reply_markup=keyboard_for_balance)

        sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
        balance = sql.fetchone()[0]
        await bot.answer_callback_query(call.id, f'Ваш текущий баланс {balance} ₽')
        one = InlineKeyboardButton("Играем!", callback_data=bet_caption)
        two = InlineKeyboardButton("Другая ставка!", callback_data='darts')
        three = InlineKeyboardButton("Другая игра", callback_data='other_game')
        keyboard_choice = InlineKeyboardMarkup().add(one, two)
        keyboard_choice.row(three)
        await call.message.answer("Играем ещё в 🎯 на ставку " + str(math.floor(balance * bets)) + ' ₽ ?',
                                  reply_markup=keyboard_choice)


@dp.callback_query_handler(lambda c: c.data == 'other_game')
async def other_games(call: CallbackQuery):
    dice = InlineKeyboardButton('Игра "Кости" 🎲', callback_data="kosti")
    darts = InlineKeyboardButton('Игра "Дартс" 🎯', callback_data="darts")
    bandit = InlineKeyboardButton('Игра "Однорукий бандит" 🎰', callback_data="bandit")
    door = InlineKeyboardButton('Игра "3 Двери" 🚪', callback_data="door")
    keyboard_game = InlineKeyboardMarkup()
    keyboard_game.row(dice, darts)
    keyboard_game.row(bandit)
    keyboard_game.row(door)
    await call.message.answer("Выбирай игру и выигрывай 💵!", reply_markup=keyboard_game)


@dp.callback_query_handler(lambda c: c.data == 'b120')
async def b120(call: CallbackQuery):
    sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
    balance = sql.fetchone()[0]
    if balance > 120:
        await sleep(0.2)
        await call.message.answer("Крутим...")
        user_value = await bot.send_dice(call.from_user.id, emoji="🎰")
        user_value = user_value['dice']['value']
        await sleep(2.3)
        if user_value == 1 or user_value == 22 or user_value == 43 or user_value == 64:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance += 3500
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Джекпот!", reply_markup=keyboard_for_balance)
        else:
            sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
            balance = sql.fetchone()[0]
            balance -= 120
            sql.execute(f"UPDATE users SET balance = {balance} WHERE user_id = {call.from_user.id}")
            db.commit()
            button_balance = KeyboardButton(f'Ваш баланс: {balance} ₽')
            keyboard_for_balance = ReplyKeyboardMarkup(resize_keyboard=True).add(button_balance)
            await call.message.answer("Проиграли...", reply_markup=keyboard_for_balance)
        await bot.answer_callback_query(call.id, f'Ваш текущий баланс {balance} ₽')
        sql.execute(f"SELECT balance FROM users WHERE user_id = {call.from_user.id}")
        balance = sql.fetchone()[0]
        if balance > 120:
            one = InlineKeyboardButton("Играем!", callback_data='b120')
            two = InlineKeyboardButton("Другая игра", callback_data='other_game')
            keyboard_choice = InlineKeyboardMarkup().add(one, two)
            await call.message.answer("Играем ещё в 🎰 на ставку 120 ₽ ?", reply_markup=keyboard_choice)
        else:
            await call.message.answer("Закончились деньги! /reset_balance")
    else:
        await call.message.answer("У вас недостаточно денег!")