from aiogram import Router, Bot
from aiogram.types import Message
from aiogram import F

helper_router = Router()

@helper_router.message(F.chat.id == -1003627692695, F.message_thread_id == 237, F.reply_to_message)
async def helper_reply(message: Message, bot: Bot):
    replied_msg = message.reply_to_message   
    if replied_msg and 'ЗАЯВКА НА УДАЛЕНИЕ' in replied_msg.text:
        lines = replied_msg.text.split('\n')
        user_id_line = next((line for line in lines if 'ID:' in line), '')
        if 'ID:' in user_id_line:
            user_id = user_id_line.split('ID:')[1].strip().replace('<code>', '').replace('</code>', '')
            if message.text:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=f'📨 <b>Ответ от администратора:</b>\n\n{message.text}',
                    parse_mode='HTML')
                await message.reply('✅ Ответ отправлен пользователю')

@helper_router.message(F.chat.id == -1003627692695, F.message_thread_id == 232, F.reply_to_message)
async def post_reply(message: Message, bot: Bot):
    from app import post_user_map
    if not message.reply_to_message:
        return
    replied_msg = message.reply_to_message
    replied_msg_id = replied_msg.message_id
    if replied_msg_id in post_user_map:
        user_id = post_user_map[replied_msg_id]
        if message.text:
            await bot.send_message(
                chat_id=int(user_id),
                text=f'📨 <b>Ответ от администратора на ваш пост:</b>\n\n{message.text}',
                parse_mode='HTML')
            await message.reply('✅ Ответ отправлен автору поста')from aiogram import Router, Bot
from aiogram.types import Message
from aiogram import F

helper_router = Router()

@helper_router.message(F.chat.id == -1003627692695, F.message_thread_id == 237, F.reply_to_message)
async def helper_reply(message: Message, bot: Bot):
    replied_msg = message.reply_to_message   
    if replied_msg and 'ЗАЯВКА НА УДАЛЕНИЕ' in replied_msg.text:
        lines = replied_msg.text.split('\n')
        user_id_line = next((line for line in lines if 'ID:' in line), '')
        if 'ID:' in user_id_line:
            user_id = user_id_line.split('ID:')[1].strip().replace('<code>', '').replace('</code>', '')
            if message.text:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=f'📨 <b>Ответ от администратора:</b>\n\n{message.text}',
                    parse_mode='HTML')
                await message.reply('✅ Ответ отправлен пользователю')

@helper_router.message(F.chat.id == -1003627692695, F.message_thread_id == 232, F.reply_to_message)
async def post_reply(message: Message, bot: Bot):
    from app import post_user_map
    if not message.reply_to_message:
        return
    replied_msg = message.reply_to_message
    replied_msg_id = replied_msg.message_id
    if replied_msg_id in post_user_map:
        user_id = post_user_map[replied_msg_id]
        if message.text:
            await bot.send_message(
                chat_id=int(user_id),
                text=f'📨 <b>Ответ от администратора на ваш пост:</b>\n\n{message.text}',
                parse_mode='HTML')
            await message.reply('✅ Ответ отправлен автору поста')
