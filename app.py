import logging
import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardRemove
from dotenv import load_dotenv
from database import db

load_dotenv()

GROUP_ID = -1003607675754

async def remove_keyboard_in_group(bot: Bot):
    try:
        msg = await bot.send_message(chat_id=GROUP_ID, text='.', reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.5)
        await bot.delete_message(chat_id=GROUP_ID, message_id=msg.message_id)
        print("✅ Клавиатура удалена из группы")
    except Exception as e:
        print(f"⚠️ Не удалось удалить клавиатуру: {e}")

async def main():
    token = os.getenv('TOKEN')
    if not token:
        print("❌ TOKEN не найден в .env файле")
        sys.exit(1)
    bot = Bot(token=token)
    
    await remove_keyboard_in_group(bot)
    
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
        db.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(main())
