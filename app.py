import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()

post_user_map = {}

# Увеличьте уровень логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    token = os.getenv('TOKEN')
    if not token:
        logger.error("❌ TOKEN не найден в .env файле")
        sys.exit(1)
    
    logger.info(f"Токен получен: {token[:10]}...")
    bot = Bot(token=token)
    dp = Dispatcher()

    logger.info("Импортируем роутеры...")
    from пользователи.helper import helper_router
    from пользователи.user import user, meme_router
    
    dp.include_router(user)
    dp.include_router(helper_router)
    dp.include_router(meme_router)  
    
    logger.info("✅ Бот запущен...")
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
