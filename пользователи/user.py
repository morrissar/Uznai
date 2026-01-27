import asyncio
from datetime import datetime
from aiogram.types import Message
from aiogram import Router, Bot
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F

import кнопки.keyboards as kb
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

CHANNEL_ID = -1003550629921

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
    except Exception:
        return False

@user.message(CommandStart())
async def start(message: Message, bot: Bot):
    if not await check_subscription(message.from_user.id, bot):
        await message.answer(
            "❌ Для использования бота необходимо подписаться на канал <a href='https://t.me/yznay138'>Узнай за УИ</a>\n\nПодпишитесь и нажмите /start снова.", 
            parse_mode='HTML'
        )
        return
    
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.', 
    reply_markup=kb.main)

async def check_subscription_wrapper(message: Message, bot: Bot) -> bool:
    """Обертка для проверки подписки в хэндлерах"""
    if not await check_subscription(message.from_user.id, bot):
        await message.answer(
            "❌ Для использования бота необходимо подписаться на канал <a href='https://t.me/yznay138'>Узнай за УИ</a>\n\nПодпишитесь и нажмите /start снова.", 
            parse_mode='HTML'
        )
        return False
    return True

@user.message(F.text == 'Контакты руководства')
async def contacts(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer(
    '<b>📞 Контакты руководства</b>\n\n'
    'Для оперативного решения вопросов обратитесь к нужному специалисту:\n\n'
    '👑 <b>Владелец канала</b>\n'
    '• Вопросы публикаций и модерации\n'
    '• Реклама и сотрудничество\n'
    '• Общие вопросы по каналу\n'
    '➜ @YznaizaYI\n\n'
    '⚙️ <b>Технический администратор</b>\n'
    '• Работа бота и технические сбои\n'
    '• Вопросы по Пользовательскому соглашению\n'
    '• Предложения по доработке функционала\n'
    '➜ @morisar_official',
    parse_mode='HTML')

@user.message(F.text == 'Пользовательское соглашение')
async def soglash(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('📜 Вот ссылка на Пользовательское соглашение: https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-01-25-31', 
    reply_markup=kb.after_soglash)

predlozhit_post_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Назад в меню')]
    ], 
    resize_keyboard=True, 
    input_field_placeholder='Отправьте ваш пост')

@user.message(F.text == 'Предложить пост')
async def make_post(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('👁️ Если Вы гарантируете, что прочли <i>Пользовательское соглашение</i>, то мы ожидаем ваш пост! Он сразу же отправится на модерацию.',
    reply_markup=predlozhit_post_keyboard,
    parse_mode='HTML')
    await state.set_state(PostStates.waiting_for_post)

@user.message(F.text == 'Удалить пост')
async def delete_post(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    
    await message.bot.send_chat_action(chat_id=message.from_user.id, action=ChatAction.TYPING)
    await message.answer('🗑️ <b>Выберите тип удаления:</b>\n\n'
                         '💎 <b>Платное удаление</b> (15 звезд)\n'
                         '• Быстро и гарантированно\n'
                         '📝 <b>Бесплатное удаление</b> (по заявке)\n'
                         'Выберите вариант:',
                         reply_markup=kb.after_udali,
                         parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_choice)

@user.message(DeleteStates.waiting_for_choice, F.text == 'Платное удаление')
async def platnoe_udal(message: Message, state: FSMContext, bot: Bot):
    await message.answer('💎 <b>Платное удаление - 15 звезд</b>\n\n'
                         'Для удаления поста оплатите 15 звезд\n'
                         'Владелец: @YznaizaYI',
                         parse_mode='HTML')
    await state.clear()
    await message.answer('🔙 Возвращаемся в главное меню...', reply_markup=kb.main)

back_only_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Назад в меню')]],
    resize_keyboard=True,
    input_field_placeholder='Заполняйте анкету')

@user.message(DeleteStates.waiting_for_choice, F.text == 'Бесплатное удаление')
async def besplat_udal(message: Message, state: FSMContext, bot: Bot):
    anketa = ('📋 <b>Заполните следующую анкету:</b>\n\n'
              '1. Ваше ФИ и возраст\n'
              '2. Причина удаления (3+ аргумента)\n'
              '3. Ваш юз в телеграмм\n'
              '4. Ссылка на пост\n'
              '5. Если пост связан с вами нам нужно удостовериться что это вы(отправьте фото). Если не с вами то отправлять не нужно\n'
              '6. Дата подачи запроса\n'
              '7. Точное время подачи запроса\n\n'
              'Отправьте всю информацию одним сообщением.')
    await message.answer(anketa, 
                         reply_markup=back_only_keyboard,
                         parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_anketa)

@user.message(DeleteStates.waiting_for_anketa)
async def process_anketa(message: Message, state: FSMContext, bot: Bot):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('❌ Заполнение анкеты отменено.',
                             reply_markup=kb.main)
        return   
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else 'без username'
    full_name = message.from_user.full_name    
    admin_text = (f'📨 <b>ЗАЯВКА НА УДАЛЕНИЕ</b>\n'
                  f'👤 От: {full_name}\n'
                  f'🔗 {username} | ID: <code>{user_id}</code>\n'
                  f'📅 {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n'
                  f'➖➖➖➖➖➖➖➖➖➖\n'
                  f'{message.text}\n')    
    await bot.send_message(chat_id=-1003627692695,
                           message_thread_id=237,
                           text=admin_text,
                           parse_mode='HTML')
    await message.answer('✅ <b>Заявка отправлена!</b>',
                         reply_markup=kb.main,
                         parse_mode='HTML')
    await state.clear()

@user.message(F.text == 'Назад в меню')
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.',
                         reply_markup=kb.main)

@user.message(PostStates.waiting_for_post)
async def process_any_post(message: Message, state: FSMContext, bot: Bot):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('👋 Привет! Мы - "Узнай за УИ"!\nДля ознакомления с функционалом бота посмотрите на кнопки.',
                             reply_markup=kb.main)
        return
    
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else 'без username'
    full_name = message.from_user.full_name
    admin_info = (f'📨 <b>ПОСТ НА МОДЕРАЦИЮ</b>\n'
                  f'👤 Отправитель: {full_name}\n'
                  f'🔗 {username} | ID: <code>{user_id}</code>\n'
                  f'📅 {message.date.strftime("%d.%m.%Y %H:%M:%S")}')
    
    if message.text:
        quoted_text = f'<blockquote expandable>{message.text}</blockquote>'
        new_text = quoted_text + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_message(chat_id=-1003627692695, message_thread_id=232, text=new_text, parse_mode='HTML', disable_web_page_preview=True)
    elif message.photo and message.caption:
        new_caption = message.caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_photo(chat_id=-1003627692695, message_thread_id=232, photo=message.photo[-1].file_id, caption=new_caption, parse_mode='HTML')
    elif message.photo:
        post_msg = await bot.send_photo(chat_id=-1003627692695, message_thread_id=232, photo=message.photo[-1].file_id, caption="<a href='https://t.me/yznay138'>Узнай за УИ</a>", parse_mode='HTML')
    elif message.video and message.caption:
        new_caption = message.caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_video(chat_id=-1003627692695, message_thread_id=232, video=message.video.file_id, caption=new_caption, parse_mode='HTML')
    elif message.video:
        post_msg = await bot.send_video(chat_id=-1003627692695, message_thread_id=232, video=message.video.file_id, caption="<a href='https://t.me/yznay138'>Узнай за УИ</a>", parse_mode='HTML')
    else:
        post_msg = await bot.copy_message(chat_id=-1003627692695, from_chat_id=message.chat.id, message_id=message.message_id, message_thread_id=232)
    
    await bot.send_message(chat_id=-1003627692695, message_thread_id=232, text=admin_info, parse_mode='HTML', reply_to_message_id=post_msg.message_id)
    
    await message.answer('✅ <b>Пост отправлен на модерацию!</b>\nАдминистратор проверит его в ближайшее время.', 
                         reply_markup=kb.main, 
                         parse_mode='HTML')
    await state.clear()

@user.message(F.chat.id == -1003607675754) 
async def on_group_message(message: Message, bot: Bot):
    if message.sender_chat and message.sender_chat.id == -1003550629921: 
        text = '📨 Опубликовать/удалить пост или написать админам - @UznaiZaUI_bot'
        await bot.send_message(chat_id=-1003607675754,
            reply_to_message_id=message.message_id,
            text=text,
            parse_mode='HTML')