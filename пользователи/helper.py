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
                    text=f'📨 <b>Ответ от администратора на ваш предложенный пост:</b>\n\n{message.text}',
                    parse_mode='HTML')
                await message.reply('✅ Ответ отправлен пользователю')

@helper_router.message(F.chat.id == -1003627692695, F.message_thread_id == 232, F.reply_to_message)
async def post_reply(message: Message, bot: Bot):
    replied_msg = message.reply_to_message
    if replied_msg and replied_msg.reply_to_message:
        admin_msg = replied_msg.reply_to_message
        if admin_msg and 'ПОСТ НА МОДЕРАЦИЮ' in admin_msg.text:
            lines = admin_msg.text.split('\n')
            user_id_line = next((line for line in lines if 'ID:' in line), '')
            if 'ID:' in user_id_line:
                user_id = user_id_line.split('ID:')[1].strip().replace('<code>', '').replace('</code>', '')
                if message.text:
                    await bot.send_message(
                        chat_id=int(user_id),
                        text=f'📨 <b>Ответ от администратора на ваш пост:</b>\n\n{message.text}',
                        parse_mode='HTML')
                    await message.reply('✅ Ответ отправлен автору поста')
