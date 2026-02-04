import asyncio
import random
import os
from datetime import datetime
from aiogram.types import Message, FSInputFile
from aiogram import Router, Bot
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
import кнопки.keyboards as kb
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging

logger = logging.getLogger(__name__)

CHANNEL_ID = -1003550629921

class PostStates(StatesGroup):
    waiting_for_post = State()

class DeleteStates(StatesGroup):
    waiting_for_choice = State()
    waiting_for_anketa = State()

user = Router()

meme_router = Router()
ALLOWED_CHATS = [-1003627692695, -1003607675754]
MEMES_FOLDER = "memes"

@meme_router.message(F.text.lower() == "мем")
async def send_meme(message: Message, bot: Bot):
    if message.chat.id not in ALLOWED_CHATS:
        return
    
    if not os.path.exists(MEMES_FOLDER):
        await message.answer("❌ Папка 'memes' не найдена!")
        return
    
    memes = [file for file in os.listdir(MEMES_FOLDER) if file.lower().endswith('.jpg')]
    
    if not memes:
        await message.answer("❌ Нет мемов в папке 'memes'!")
        return
    
    random_meme = random.choice(memes)
    meme_path = os.path.join(MEMES_FOLDER, random_meme)
    photo = FSInputFile(meme_path)
    
    # Если сообщение пришло из топика, отвечаем в тот же топик
    if message.message_thread_id:
        # Отправляем в тот же топик, откуда пришло сообщение
        await bot.send_photo(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            photo=photo,
            caption="🤡 Ваш мем!"
        )
    elif message.chat.id == -1003627692695:
        # Если нет топика, но это чат с топиками, отправляем в топик 1
        await bot.send_photo(
            chat_id=message.chat.id,
            message_thread_id=1,
            photo=photo,
            caption="🤡 Ваш мем!"
        )
    else:
        # Обычный чат без топиков
        await message.answer_photo(photo, caption="🤡 Ваш мем!")
        
@user.message(CommandStart())
async def start(message: Message, bot: Bot):
    if not await check_subscription(message.from_user.id, bot):
        await message.answer("❌ Для использования бота необходимо подписаться на канал <a href='https://t.me/yznay138'>Узнай за УИ</a>\n\nПодпишитесь и нажмите /start снова.", parse_mode='HTML')
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.', reply_markup=kb.main)

async def check_subscription_wrapper(message: Message, bot: Bot) -> bool:
    if not await check_subscription(message.from_user.id, bot):
        await message.answer("❌ Для использования бота необходимо подписаться на канал <a href='https://t.me/yznay138'>Узнай за УИ</a>\n\nПодпишитесь и нажмите /start снова.", parse_mode='HTML')
        return False
    return True

@user.message(F.text == 'Контакты руководства')
async def contacts(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('<b>📞 Контакты руководства</b>\n\nДля оперативного решения вопросов обратитесь к нужному специалисту:\n\n👑 <b>Владелец канала</b>\n• Вопросы публикаций и модерации\n• Реклама и сотрудничество\n• Общие вопросы по каналу\n➜ @YznaizaYI\n\n⚙️ <b>Технический администратор</b>\n• Работа бота и технические сбои\n• Вопросы по Пользовательскому соглашению\n• Предложения по доработке функционала\n➜ @morisar_official',parse_mode='HTML')

@user.message(F.text == 'Пользовательское соглашение')
async def soglash(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('📜 Вот ссылка на Пользовательское соглашение: https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-01-25-31', reply_markup=kb.after_soglash)

predlozhit_post_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад в меню')]], resize_keyboard=True, input_field_placeholder='Отправьте ваш пост')

@user.message(F.text == 'Предложить пост')
async def make_post(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('👁️ Если Вы гарантируете, что прочли <i>Пользовательское соглашение</i>, то мы ожидаем ваш пост! Он сразу же отправится на модерацию.',reply_markup=predlozhit_post_keyboard,parse_mode='HTML')
    await state.set_state(PostStates.waiting_for_post)

@user.message(F.text == 'Удалить пост')
async def delete_post(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('🗑️ <b>Выберите тип удаления:</b>\n\n💎 <b>Платное удаление</b> (15 звезд)\n• Быстро и гарантированно\n📝 <b>Бесплатное удаление</b> (по заявке)\nВыберите вариант:',reply_markup=kb.after_udali,parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_choice)

@user.message(DeleteStates.waiting_for_choice, F.text == 'Платное удаление')
async def platnoe_udal(message: Message, state: FSMContext, bot: Bot):
    await message.answer('💎 <b>Платное удаление - 15 звезд</b>\n\nДля удаления поста оплатите 15 звезд\nВладелец: @YznaizaYI',parse_mode='HTML')
    await state.clear()
    await message.answer('🔙 Возвращаемся в главное меню...', reply_markup=kb.main)

back_only_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад в меню')]],resize_keyboard=True,input_field_placeholder='Заполняйте анкету')

@user.message(DeleteStates.waiting_for_choice, F.text == 'Бесплатное удаление')
async def besplat_udal(message: Message, state: FSMContext, bot: Bot):
    anketa = ('📋 <b>Заполните следующую анкету:</b>\n\n1. Ваше ФИ и возраст\n2. Причина удаления (3+ аргумента)\n3. Ваш юз в телеграмм\n4. Ссылка на пост\n5. Если пост связан с вами нам нужно удостовериться что это вы(отправьте фото). Если не с вами то отправлять не нужно\n6. Дата подачи запроса\n7. Точное время подачи запроса\n\nОтправьте всю информацию одним сообщением.')
    await message.answer(anketa, reply_markup=back_only_keyboard, parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_anketa)

@user.message(DeleteStates.waiting_for_anketa)
async def process_anketa(message: Message, state: FSMContext, bot: Bot):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('❌ Заполнение анкеты отменено.',reply_markup=kb.main)
        return   
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else 'без username'
    full_name = message.from_user.full_name    
    admin_text = (f'📨 <b>ЗАЯВКА НА УДАЛЕНИЕ</b>\n👤 От: {full_name}\n🔗 {username} | ID: <code>{user_id}</code>\n📅 {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n➖➖➖➖➖➖➖➖➖➖\n{message.text}\n')    
    await bot.send_message(chat_id=-1003627692695,message_thread_id=237,text=admin_text,parse_mode='HTML')
    await message.answer('✅ <b>Заявка отправлена!</b>',reply_markup=kb.main,parse_mode='HTML')
    await state.clear()

@user.message(F.text == 'Назад в меню')
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.',reply_markup=kb.main)

@user.message(PostStates.waiting_for_post)
async def process_any_post(message: Message, state: FSMContext, bot: Bot):
    from app import post_user_map
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.',reply_markup=kb.main)
        return
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else 'без username'
    full_name = message.from_user.full_name
    admin_info = (f'📨 <b>ПОСТ НА МОДЕРАЦИЮ</b>\n👤 Отправитель: {full_name}\n🔗 {username} | ID: <code>{user_id}</code>\n📅 {message.date.strftime("%d.%m.%Y %H:%M:%S")}')
    if message.text:
        quoted_text = f'<blockquote expandable>{message.text}</blockquote>'
        new_text = quoted_text + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_message(chat_id=-1003627692695, message_thread_id=232, text=new_text, parse_mode='HTML', disable_web_page_preview=True)
        post_user_map[post_msg.message_id] = user_id
    elif message.photo and message.caption:
        new_caption = message.caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_photo(chat_id=-1003627692695, message_thread_id=232, photo=message.photo[-1].file_id, caption=new_caption, parse_mode='HTML')
        post_user_map[post_msg.message_id] = user_id
    elif message.photo:
        post_msg = await bot.send_photo(chat_id=-1003627692695, message_thread_id=232, photo=message.photo[-1].file_id, caption="<a href='https://t.me/yznay138'>Узнай за УИ</a>", parse_mode='HTML')
        post_user_map[post_msg.message_id] = user_id    
    elif message.video and message.caption:
        new_caption = message.caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_video(chat_id=-1003627692695, message_thread_id=232, video=message.video.file_id, caption=new_caption, parse_mode='HTML')
        post_user_map[post_msg.message_id] = user_id    
    elif message.video:
        post_msg = await bot.send_video(chat_id=-1003627692695, message_thread_id=232, video=message.video.file_id, caption="<a href='https://t.me/yznay138'>Узнай за УИ</a>", parse_mode='HTML')
        post_user_map[post_msg.message_id] = user_id
    else:
        post_msg = await bot.copy_message(chat_id=-1003627692695, from_chat_id=message.chat.id, message_id=message.message_id, message_thread_id=232)
        post_user_map[post_msg.message_id] = user_id
    await bot.send_message(chat_id=-1003627692695, message_thread_id=232, text=admin_info, parse_mode='HTML', reply_to_message_id=post_msg.message_id)
    await message.answer('✅ <b>Пост отправлен на модерацию!</b>\nАдминистратор проверит его в ближайшее время.', reply_markup=kb.main, parse_mode='HTML')
    await state.clear()

@user.message(F.chat.id == -1003607675754) 
async def on_group_message(message: Message, bot: Bot):
    if message.sender_chat and message.sender_chat.id == -1003550629921: 
        text = '📨 Опубликовать/удалить пост или написать админам - @UznaiZaUI_bot'
        await bot.send_message(chat_id=-1003607675754,reply_to_message_id=message.message_id,text=text,parse_mode='HTML')


