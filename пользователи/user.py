import random
import os
import json
import asyncio
from datetime import datetime
from aiogram import Bot, Router, F
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import кнопки.keyboards as kb
from database import db

CHANNEL_ID = -1003550629921
GROUP_ID = -1003607675754
ADMIN_GROUP_ID = -1003710242278
MY_AND_VLD_GROUP_ID = -1003620787834

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

post_user_map = load_json_map(POST_MAP_FILE)
delete_user_map = load_json_map(DELETE_MAP_FILE)

class PostStates(StatesGroup):
    waiting_for_post = State()

class DeleteStates(StatesGroup):
    waiting_for_choice = State()
    waiting_for_anketa = State()

user = Router()

async def check_subscription(user_id: int, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def ensure_subscription(message: Message, bot: Bot) -> bool:
    if not await check_subscription(message.from_user.id, bot):
        await message.answer("❌ Для использования бота необходимо подписаться на канал <a href='https://t.me/yznay138'>Узнай за УИ</a>\n\nПодпишитесь и нажмите /start снова.", parse_mode='HTML')
        return False
    return True

def record_user(message: Message):
    username = f'@{message.from_user.username}' if message.from_user.username else None
    db.add_or_update_user(message.from_user.id, username, message.from_user.full_name)

@user.message(F.text.lower() == "мем")
async def send_meme(message: Message, bot: Bot):
    if message.chat.id != GROUP_ID:
        return
    if not os.path.exists("memes"):
        return
    memes = [f for f in os.listdir("memes") if f.lower().endswith('.jpg')]
    if not memes:
        return
    random_meme = random.choice(memes)
    meme_path = os.path.join("memes", random_meme)
    photo = FSInputFile(meme_path)
    await bot.send_photo(chat_id=message.chat.id, photo=photo, caption="🤡 Ваш мем!")

@user.message(CommandStart())
async def start(message: Message, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    record_user(message)
    if not await ensure_subscription(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.', reply_markup=kb.main)

@user.message(F.text == 'Контакты руководства')
async def contacts(message: Message, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    record_user(message)
    if not await ensure_subscription(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('<b>📞 Контакты руководства</b>\n\nДля оперативного решения вопросов обратитесь к нужному специалисту:\n\n👑 <b>Владелец канала</b>\n• Вопросы публикаций и модерации\n• Реклама и сотрудничество\n• Общие вопросы по каналу\n➜ @YznaizaYI\n\n⚙️ <b>Технический администратор</b>\n• Работа бота и технические сбои\n• Вопросы по Пользовательскому соглашению\n• Предложения по доработке функционала\n➜ @morisar_official', parse_mode='HTML')

@user.message(F.text == 'Пользовательское соглашение')
async def soglash(message: Message, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    record_user(message)
    if not await ensure_subscription(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('📜 Вот ссылка на Пользовательское соглашение: https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-01-25-31', reply_markup=kb.after_soglash)

@user.message(F.text == 'Предложить пост')
async def make_post(message: Message, state: FSMContext, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    record_user(message)
    if not await ensure_subscription(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('👁️ Если Вы гарантируете, что прочли <i>Пользовательское соглашение</i>, то мы ожидаем ваш пост! Он сразу же отправится на модерацию.', reply_markup=kb.back_keyboard, parse_mode='HTML')
    await state.set_state(PostStates.waiting_for_post)

@user.message(F.text == 'Удалить пост')
async def delete_post(message: Message, state: FSMContext, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    record_user(message)
    if not await ensure_subscription(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('🗑️ <b>Выберите тип удаления:</b>\n\n💎 <b>Платное удаление</b> (15 звезд)\n• Быстро и гарантированно\n📝 <b>Бесплатное удаление</b> (по заявке)\nВыберите вариант:', reply_markup=kb.after_udali, parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_choice)

@user.message(DeleteStates.waiting_for_choice, F.text == 'Платное удаление')
async def platnoe_udal(message: Message, state: FSMContext, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    await message.answer('💎 <b>Платное удаление - 15 звезд</b>\n\nДля удаления поста отправьте подарок стоимостью 15 звезд.\nВладелец: @YznaizaYI', parse_mode='HTML')
    await state.clear()
    await message.answer('🔙 Возвращаемся в главное меню...', reply_markup=kb.main)

@user.message(DeleteStates.waiting_for_choice, F.text == 'Бесплатное удаление')
async def besplat_udal(message: Message, state: FSMContext, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    anketa = ('📋 <b>Заполните следующую анкету:</b>\n\n1. Ваше ФИ и возраст\n2. Причина удаления (3+ аргумента)\n3. Ваш юз в телеграмм\n4. Ссылка на пост\n5. Дата подачи запроса\n6. Точное время подачи запроса\n\nОтправьте всю информацию одним сообщением.')
    await message.answer(anketa, reply_markup=kb.back_keyboard, parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_anketa)

@user.message(DeleteStates.waiting_for_anketa)
async def process_anketa(message: Message, state: FSMContext, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('❌ Заполнение анкеты отменено.', reply_markup=kb.main)
        return
    db.increment_delete_requests(message.from_user.id)
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else 'без username'
    full_name = message.from_user.full_name
    admin_text = (f'📨 <b>ЗАЯВКА НА УДАЛЕНИЕ</b>\n👤 От: {full_name}\n🔗 {username} | ID: <code>{user_id}</code>\n📅 {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n➖➖➖➖➖➖➖➖➖➖\n{message.text}\n')
    sent_msg = await bot.send_message(chat_id=ADMIN_GROUP_ID, message_thread_id=37, text=admin_text, parse_mode='HTML')
    delete_user_map[str(sent_msg.message_id)] = str(user_id)
    save_json_map(delete_user_map, DELETE_MAP_FILE)
    await message.answer('✅ <b>Заявка отправлена!</b>', reply_markup=kb.main, parse_mode='HTML')
    await state.clear()

@user.message(F.text == 'Назад в меню')
async def back_to_menu(message: Message, state: FSMContext):
    if message.chat.id == GROUP_ID:
        return
    await state.clear()
    await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.', reply_markup=kb.main)

@user.message(PostStates.waiting_for_post)
async def process_any_post(message: Message, state: FSMContext, bot: Bot):
    if message.chat.id == GROUP_ID:
        return
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.', reply_markup=kb.main)
        return
    db.increment_posts_count(message.from_user.id)
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else 'без username'
    full_name = message.from_user.full_name
    admin_info = (f'\n\n📨 <b>ИНФОРМАЦИЯ ОБ АВТОРЕ</b>\n'
                  f'👤 Отправитель: {full_name}\n'
                  f'🔗 {username} | ID: <code>{user_id}</code>\n'
                  f'📅 {message.date.strftime("%d.%m.%Y %H:%M:%S")}')
    if message.text:
        quoted_text = f'<blockquote expandable>{message.text}</blockquote>'
        new_text = quoted_text + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg_admin = await bot.send_message(chat_id=ADMIN_GROUP_ID, message_thread_id=2, text=new_text, parse_mode='HTML', disable_web_page_preview=True)
    elif message.photo:
        caption = message.caption if message.caption else ""
        new_caption = caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg_admin = await bot.send_photo(chat_id=ADMIN_GROUP_ID, message_thread_id=2, photo=message.photo[-1].file_id, caption=new_caption, parse_mode='HTML')
    elif message.video:
        caption = message.caption if message.caption else ""
        new_caption = caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg_admin = await bot.send_video(chat_id=ADMIN_GROUP_ID, message_thread_id=2, video=message.video.file_id, caption=new_caption, parse_mode='HTML')
    else:
        post_msg_admin = await bot.copy_message(chat_id=ADMIN_GROUP_ID, from_chat_id=message.chat.id, message_id=message.message_id, message_thread_id=2)
    post_user_map[str(post_msg_admin.message_id)] = str(user_id)
    save_json_map(post_user_map, POST_MAP_FILE)
    if message.text:
        quoted_text = f'<blockquote expandable>{message.text}</blockquote>'
        full_text = quoted_text + admin_info
        await bot.send_message(chat_id=MY_AND_VLD_GROUP_ID, text=full_text, parse_mode='HTML')
    elif message.photo:
        caption = message.caption if message.caption else ""
        full_caption = caption + admin_info
        await bot.send_photo(chat_id=MY_AND_VLD_GROUP_ID, photo=message.photo[-1].file_id, caption=full_caption, parse_mode='HTML')
    elif message.video:
        caption = message.caption if message.caption else ""
        full_caption = caption + admin_info
        await bot.send_video(chat_id=MY_AND_VLD_GROUP_ID, video=message.video.file_id, caption=full_caption, parse_mode='HTML')
    else:
        await bot.copy_message(chat_id=MY_AND_VLD_GROUP_ID, from_chat_id=message.chat.id, message_id=message.message_id)
        await bot.send_message(chat_id=MY_AND_VLD_GROUP_ID, text=admin_info, parse_mode='HTML')
    await message.answer('✅ <b>Пост отправлен на модерацию!</b>\nАдминистратор проверит его в ближайшее время.', reply_markup=kb.main, parse_mode='HTML')
    await state.clear()

@user.message(F.chat.id == GROUP_ID)
async def on_group_message(message: Message, bot: Bot):
    if message.sender_chat and message.sender_chat.id == CHANNEL_ID:
        text = '📨 Опубликовать/удалить пост или написать админам - @UznaiZaUI_bot'
        await bot.send_message(chat_id=GROUP_ID, reply_to_message_id=message.message_id, text=text, parse_mode='HTML')

async def remove_keyboard_in_group(bot: Bot):
    try:
        remove_msg = await bot.send_message(chat_id=GROUP_ID, text='⌨️ Клавиатура удалена', reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(1)
        await bot.delete_message(chat_id=GROUP_ID, message_id=remove_msg.message_id)
    except Exception as e:
        print(f"Не удалось удалить клавиатуру в группе: {e}")
