import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from пользователи.helper import helper_router
load_dotenv()
from пользователи.user import user

post_user_map = {}

async def main():
    token = os.getenv('TOKEN')
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(user)
    dp.include_router(helper_router)    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())
