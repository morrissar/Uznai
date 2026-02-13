import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

async def main():
    token = os.getenv('TOKEN')
    if not token:
        print("❌ TOKEN не найден в .env файле")
        sys.exit(1)
    
    bot = Bot(token=token)
    dp = Dispatcher()

    from пользователи.user import user
    from пользователи.helper import helper_router
    
    dp.include_router(user)
    dp.include_router(helper_router)
    
    print("✅ Бот запущен...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())
