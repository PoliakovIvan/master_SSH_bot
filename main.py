from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import asyncio
import os
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from db import init_db
from sqlalchemy.ext.asyncio import AsyncSession
from handlers import register_handlers

load_dotenv()

async def main():
    bot = Bot(
        token=os.getenv("TG_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Ініціалізація бази даних
    await init_db()

    register_handlers(dp)


    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
