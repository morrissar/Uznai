from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
import json
import os
from database import db

helper_router = Router()

POST_MAP_FILE = 'post_user_map.json'
DELETE_MAP_FILE = 'delete_user_map.json'

def load_json_map(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@helper_router.message(F.chat.id == -1003710242278, F.message_thread_id == 37, F.reply_to_message)
async def helper_reply(message: Message, bot: Bot):
    replied_msg = message.reply_to_message
    delete_map = load_json_map(DELETE_MAP_FILE)
    replied_msg_id = str(replied_msg.message_id)
    if replied_msg_id in delete_map:
        user_id = delete_map[replied_msg_id]
        await bot.send_message(chat_id=int(user_id), text=f'📨 <b>Ответ от администратора:</b>\n\n{message.text}', parse_mode='HTML')
        await message.reply('✅ Ответ отправлен пользователю')

@helper_router.message(F.chat.id == -1003710242278, F.message_thread_id == 2, F.reply_to_message)
async def post_reply(message: Message, bot: Bot):
    replied_msg = message.reply_to_message
    post_map = load_json_map(POST_MAP_FILE)
    replied_msg_id = str(replied_msg.message_id)
    if replied_msg_id in post_map:
        user_id = post_map[replied_msg_id]
        if message.text:
            await bot.send_message(chat_id=int(user_id), text=f'📨 <b>Ответ от администратора на ваш пост:</b>\n\n{message.text}', parse_mode='HTML')
            await message.reply('✅ Ответ отправлен автору поста')

@helper_router.message(F.chat.id == -1003620787834, F.text.startswith('/vsem'))
async def send_to_all(message: Message, bot: Bot):
    text_to_send = message.text.replace('/vsem', '', 1).strip()
    if not text_to_send and not message.photo and not message.video:
        await message.reply('плохо брат переделай')
        return
    
    cursor = db.conn.cursor()
    cursor.execute("SELECT id FROM users")
    users = cursor.fetchall()
    sent_count = 0
    failed_count = 0
    
    status_msg = await message.reply(f'Начинаю рассылку {len(users)} пользователям...')
    
    for user in users:
        try:
            if message.photo:
                if text_to_send:
                    await bot.send_photo(chat_id=user[0], photo=message.photo[-1].file_id, caption=text_to_send, parse_mode='HTML')
                else:
                    await bot.send_photo(chat_id=user[0], photo=message.photo[-1].file_id, parse_mode='HTML')
            elif message.video:
                if text_to_send:
                    await bot.send_video(chat_id=user[0], video=message.video.file_id, caption=text_to_send, parse_mode='HTML')
                else:
                    await bot.send_video(chat_id=user[0], video=message.video.file_id, parse_mode='HTML')
            else:
                await bot.send_message(chat_id=user[0], text=text_to_send, parse_mode='HTML')
            sent_count += 1
        except Exception:
            failed_count += 1
        
        if sent_count % 20 == 0:
            await status_msg.edit_text(f'Рассылка...\n Отправлено: {sent_count}\n Ошибок: {failed_count}\n Осталось: {len(users) - sent_count - failed_count}')
    
    await status_msg.edit_text(f'Рассылка завершена!\n\n Успешно: {sent_count}\n Не отправлено: {failed_count}\n Всего: {len(users)}')
