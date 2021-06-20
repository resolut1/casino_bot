import asyncio
import sqlite3
from config import token
from aiogram import Bot, Dispatcher, types, executor


db = sqlite3.connect('users.db')
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    user_id INT,
    balance BIGINT,
    status_game TEXT,
    bet BIGINT,
    rand_door INT,
    bet_caption TEXT
)""")
db.commit()

loop = asyncio.get_event_loop()

bot = Bot(token, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop)

if __name__ == "__main__":
    from handlers import dp
    executor.start_polling(dp)
