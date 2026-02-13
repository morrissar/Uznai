import re
from aiogram import Router, Bot, F
from aiogram.types import Message
import json
import os

helper_router = Router()

POST_MAP_FILE = 'post_user_map.json'
DELETE_MAP_FILE = 'delete_user_map.json'

def load_json_map(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

def save_json_map(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

@helper_router.message(F.chat.id == -1003627692695, F.message_thread_id == 237, F.reply_to_message)
async def helper_reply(message: Message, bot: Bot):
    replied_msg = message.reply_to_message
    if not replied_msg:
        return
    delete_map = load_json_map(DELETE_MAP_FILE)
    replied_msg_id = str(replied_msg.message_id)
    if replied_msg_id in delete_map:
        user_id = delete_map[replied_msg_id]
        try:
            await bot.send_message(
                chat_id=int(user_id),
                text=f'📨 <b>Ответ от администратора:</b>\n\n{message.text}',
                parse_mode='HTML'
            )
            await message.reply('✅ Ответ отправлен пользователю')
        except Exception as e:
            await message.reply(f'❌ Ошибка отправки: {e}')
    else:
        await message.reply('❌ Не удалось найти ID пользователя (возможно, данные утеряны)')

@helper_router.message(F.chat.id == -1003627692695, F.message_thread_id == 232, F.reply_to_message)
async def post_reply(message: Message, bot: Bot):
    if not message.reply_to_message:
        return
    replied_msg = message.reply_to_message
    post_map = load_json_map(POST_MAP_FILE)
    replied_msg_id = str(replied_msg.message_id)
    if replied_msg_id in post_map:
        user_id = post_map[replied_msg_id]
        if message.text:
            try:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=f'📨 <b>Ответ от администратора на ваш пост:</b>\n\n{message.text}',
                    parse_mode='HTML'
                )
                await message.reply('✅ Ответ отправлен автору поста')
            except Exception as e:
                await message.reply(f'❌ Ошибка отправки: {e}')
    else:
        await message.reply('❌ Не найден автор поста (возможно, данные утеряны)')
