import os
import json
import asyncio
from datetime import datetime, timedelta
from aiogram import Router, Bot, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from database import db

helper_router = Router()

POST_MAP_FILE = 'post_user_map.json'
DELETE_MAP_FILE = 'delete_user_map.json'

CHANNEL_ID = -1003550629921
AUTOPOST_THREAD_ID = 9926
ADMIN_GROUP_ID = -1003710242278

active_autopost_tasks = {}

class AutoPostStates(StatesGroup):
    waiting_for_count = State()
    waiting_for_posts = State()
    waiting_for_interval = State()

def load_json_map(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

async def send_scheduled_posts(bot: Bot, message_ids: list, admin_chat_id: int, interval_minutes: int, thread_id: int):
    try:
        for idx, msg_id in enumerate(message_ids):
            try:
                await bot.copy_message(
                    chat_id=CHANNEL_ID, 
                    from_chat_id=admin_chat_id, 
                    message_id=msg_id
                )
            except Exception as e:
                await bot.send_message(
                    chat_id=admin_chat_id, 
                    message_thread_id=thread_id, 
                    text=f'ошибка при отправке одного из постов: {e}'
                )

            if idx < len(message_ids) - 1:
                await asyncio.sleep(interval_minutes * 60)
                
        await bot.send_message(
            chat_id=admin_chat_id, 
            message_thread_id=thread_id, 
            text='все запланированные посты успешно опубликованы в канале!'
        )

    except asyncio.CancelledError:
        await bot.send_message(
            chat_id=admin_chat_id, 
            message_thread_id=thread_id, 
            text='процесс рассылки был принудительно остановлен.'
        )
    finally:
        if thread_id in active_autopost_tasks:
            del active_autopost_tasks[thread_id]

@helper_router.message(F.chat.id == ADMIN_GROUP_ID, F.message_thread_id == AUTOPOST_THREAD_ID, Command('start'))
async def start_autopost(message: Message, state: FSMContext):
    if AUTOPOST_THREAD_ID in active_autopost_tasks:
        await message.reply('в данный момент уже идет рассылка! остановите её командой /stop перед запуском новой.')
        return

    await state.set_state(AutoPostStates.waiting_for_count)
    await message.reply('сколько постов вы хотите отправить в очередь?')

@helper_router.message(AutoPostStates.waiting_for_count, F.chat.id == ADMIN_GROUP_ID, F.message_thread_id == AUTOPOST_THREAD_ID)
async def process_count(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.reply('пожалуйста, введите целое положительное число.')
        return
        
    count = int(message.text)
    await state.update_data(target_count=count, collected_posts=[])
    await state.set_state(AutoPostStates.waiting_for_posts)
    await message.reply(f'отлично. теперь отправьте сюда по очереди {count} постов.', parse_mode='HTML')

@helper_router.message(AutoPostStates.waiting_for_posts, F.chat.id == ADMIN_GROUP_ID, F.message_thread_id == AUTOPOST_THREAD_ID)
async def collect_posts(message: Message, state: FSMContext):
    data = await state.get_data()
    collected = data['collected_posts']
    target = data['target_count']
    
    collected.append(message.message_id)
    
    if len(collected) >= target:
        await state.update_data(collected_posts=collected)
        await state.set_state(AutoPostStates.waiting_for_interval)
        await message.reply('все посты приняты! теперь введите интервал между публикациями (в минутах):')
    else:
        await state.update_data(collected_posts=collected)

@helper_router.message(AutoPostStates.waiting_for_interval, F.chat.id == ADMIN_GROUP_ID, F.message_thread_id == AUTOPOST_THREAD_ID)
async def process_interval(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.reply('интервал должен быть целым положительным числом.')
        return
        
    interval_minutes = int(message.text)
    data = await state.get_data()
    message_ids = data['collected_posts']
    target_count = data['target_count']
    
    await state.clear()
    
    total_minutes = interval_minutes * (target_count - 1)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    time_str = ''
    if hours > 0:
        time_str += f'{hours} ч. '
    time_str += f'{minutes} мин.' if minutes > 0 or hours == 0 else ''
    
    await message.reply(
        f'<b>запускаю рассылку!</b>\n'
        f'всего постов: {target_count}\n'
        f'интервал: {interval_minutes} мин.\n'
        f'процесс займет примерно: {time_str}\n\n'
        f'<i>Для досрочной отмены напишите /stop</i>',
        parse_mode='HTML'
    )
    
    task = asyncio.create_task(
        send_scheduled_posts(
            bot=bot,
            message_ids=message_ids,
            admin_chat_id=message.chat.id,
            interval_minutes=interval_minutes,
            thread_id=AUTOPOST_THREAD_ID
        )
    )
    active_autopost_tasks[AUTOPOST_THREAD_ID] = task

@helper_router.message(F.chat.id == ADMIN_GROUP_ID, F.message_thread_id == AUTOPOST_THREAD_ID, Command('stop'))
async def stop_autopost(message: Message, state: FSMContext):
    await state.clear() 
    
    if AUTOPOST_THREAD_ID in active_autopost_tasks:
        active_autopost_tasks[AUTOPOST_THREAD_ID].cancel()
    else:
        await message.reply('в данный момент нет активных рассылок или сбора постов для остановки.')

async def check_auto_unban(bot: Bot):
    cursor = db.conn.cursor()
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('SELECT id FROM banned WHERE time_ban <= ?', (current_time_str,))
    expired_bans = cursor.fetchall()
        
    for row in expired_bans:
        user_id = row[0]
        db.unban_user(user_id=user_id)
        try:
            await bot.send_message(
                chat_id=user_id, 
                text='❗ <b>Срок вашей блокировки истёк.</b>\nВы снова можете использовать бота. Больше не нарушайте правила! ❤',
                parse_mode='HTML')
        except Exception:
            pass

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
            await bot.send_message(chat_id=int(user_id), text=f'📨 <b>Ответ от администратора на ваш post:</b>\n\n{message.text}', parse_mode='HTML')
            await message.reply('✅ Ответ отправлен автору поста')

@helper_router.message(F.chat.id == -1003620787834, F.text.startswith('/ban'))
async def ban(message: Message, bot: Bot):
    command_args = message.text.replace('/ban', '', 1).strip()
    args = command_args.split(maxsplit=2)
    
    if len(args) < 2:
        await message.reply('плохо брат переделай\nпиши так: /ban ID ВРЕМЯ ПРИЧИНА')
        return
        
    user_id_str, time_ban_str, cause = args[0], args[1], args[2]
    
    if not user_id_str.isdigit():
        await message.reply('але айди должен быть цифрами')
        return
        
    user_id = int(user_id_str)
    is_perm = time_ban_str.lower() in ['perm', 'пермач']
    
    if not is_perm and not time_ban_str.isdigit():
        await message.reply('время должно быть числом или словом perm/пермач')
        return

    if is_perm:
        exact_unban_time = '9999-12-31 23:59:59'
        text_time = 'навсегда'
    else:
        hours = int(time_ban_str)
        unban_datetime = datetime.now() + timedelta(hours=hours)
        exact_unban_time = unban_datetime.strftime('%Y-%m-%d %H:%M:%S')
        text_time = f'на {hours}ч'
    
    db.ban_user(user_id=user_id, time_ban=exact_unban_time, cause=cause)
    
    try: 
        await bot.send_message(
            chat_id=user_id, 
            text=f'❗❗❗ Вы заблокированы в боте администратором <b>{text_time}</b> по причине: <b>{cause}</b>. ❗❗❗',
            parse_mode='HTML'
        )
    except Exception:
        pass
        
    cursor = db.conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    user_name = result[0] if result else f'ID: {user_id}'
    
    await message.reply(f'Пользователь {user_name} успешно заблокирован {text_time} по причине {cause}.')

@helper_router.message(F.chat.id == -1003620787834, F.text.startswith('/unban'))
async def unban(message: Message, bot: Bot):
    user_id_str = message.text.replace('/unban', '', 1).strip()
    if not user_id_str:
        await message.reply('плохо брат переделай\nпиши так: /unban ID')
        return
        
    if not user_id_str.isdigit():
        await message.reply('але айди пиши')
        return
        
    user_id = int(user_id_str)
    db.unban_user(user_id=user_id)
    
    cursor = db.conn.cursor()
    cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    user_name = result[0] if result else f'ID: {user_id}'
    
    await message.reply(f'Пользователь {user_name} успешно разбанен.')
    
    try: 
        await bot.send_message(
            chat_id=user_id, 
            text='❗ Вы были разблокированы администратором. Больше не нарушайте наши правила ❤'
        )
    except Exception:
        pass

@helper_router.message(F.chat.id == -1003620787834, F.text.startswith('/vsem'))
async def send_to_all(message: Message, bot: Bot):
    text_to_send = message.text.replace('/vsem', '', 1).strip()
    if not text_to_send and not message.photo and not message.video:
        await message.reply('плохо брат переделай')
        return

    cursor = db.conn.cursor()
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()
    sent_count = 0
    failed_count = 0
    
    status_msg = await message.reply(f'Начинаю рассылку {len(users)} пользователям...')
    
    for user in users:
        user_id = user[0]
        try:
            if message.photo:
                if text_to_send:
                    await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=text_to_send, parse_mode='HTML')
                else:
                    await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, parse_mode='HTML')
            elif message.video:
                if text_to_send:
                    await bot.send_video(chat_id=user_id, video=message.video.file_id, caption=text_to_send, parse_mode='HTML')
                else:
                    await bot.send_video(chat_id=user_id, video=message.video.file_id, parse_mode='HTML')
            else:
                await bot.send_message(chat_id=user_id, text=text_to_send, parse_mode='HTML')
            
            sent_count += 1
            
        except Exception:
            failed_count += 1
        
        await asyncio.sleep(0.04) 
        
        if sent_count % 50 == 0:
            try:
                await status_msg.edit_text(f'Рассылка...\n Отправлено: {sent_count}\n Ошибок: {failed_count}\n Осталось: {len(users) - sent_count - failed_count}')
            except Exception:
                pass

    await status_msg.edit_text(f'Рассылка завершена!\n\n Успешно: {sent_count}\n Не отправлено: {failed_count}\n Всего: {len(users)}')
