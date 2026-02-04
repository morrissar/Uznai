import random
import os
from aiogram.types import Message, FSInputFile
from aiogram import Router, Bot
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

@user.message(F.text.lower() == "мем")
async def send_meme(message: Message, bot: Bot):
    # Только для чата -1003607675754
    if message.chat.id != -1003607675754:
        return
    
    if not os.path.exists("memes"):
        await message.answer("❌ Нет папки memes!")
        return
    
    memes = [f for f in os.listdir("memes") if f.lower().endswith('.jpg')]
    if not memes:
        await message.answer("❌ Нет мемов в папке!")
        return
    
    random_meme = random.choice(memes)
    meme_path = os.path.join("memes", random_meme)
    photo = FSInputFile(meme_path)
    
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption="🤡 Ваш мем!"
    )

async def check_subscription(user_id: int, bot: Bot) -> bool:
    member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    return member.status in ['member', 'administrator', 'creator']

@user.message(CommandStart())
async def start(message: Message, bot: Bot):
    if not await check_subscription(message.from_user.id, bot):
        await message.answer("❌ Для использования бота необходимо подписаться на канал <a href='https://t.me/yznay138'>Узнай за УИ</a>\n\nПодпишитесь и нажмите /start снова.", parse_mode='HTML')
        return
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
    await message.answer('<b>📞 Контакты руководства</b>\n\n👑 <b>Владелец канала</b>\n➜ @YznaizaYI\n\n⚙️ <b>Технический администратор</b>\n➜ @morisar_official',parse_mode='HTML')

@user.message(F.text == 'Пользовательское соглашение')
async def soglash(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.answer('📜 https://telegra.ph/POLZOVATELSKOE-SOGLASHENIE-01-25-31', reply_markup=kb.after_soglash)

@user.message(F.text == 'Предложить пост')
async def make_post(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.answer('👁️ Отправьте ваш пост!',reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад в меню')]], resize_keyboard=True),parse_mode='HTML')
    await state.set_state(PostStates.waiting_for_post)

@user.message(F.text == 'Удалить пост')
async def delete_post(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.answer('🗑️ <b>Выберите тип удаления:</b>',reply_markup=kb.after_udali,parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_choice)

@user.message(DeleteStates.waiting_for_choice, F.text == 'Платное удаление')
async def platnoe_udal(message: Message, state: FSMContext, bot: Bot):
    await message.answer('💎 <b>Платное удаление - 15 звезд</b>',parse_mode='HTML')
    await state.clear()
    await message.answer('🔙 Возвращаемся в главное меню...', reply_markup=kb.main)

@user.message(DeleteStates.waiting_for_choice, F.text == 'Бесплатное удаление')
async def besplat_udal(message: Message, state: FSMContext, bot: Bot):
    if not await check_subscription_wrapper(message, bot):
        return
    await message.answer('📋 <b>Заполните анкету:</b>', reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад в меню')]],resize_keyboard=True), parse_mode='HTML')
    await state.set_state(DeleteStates.waiting_for_anketa)

@user.message(DeleteStates.waiting_for_anketa)
async def process_anketa(message: Message, state: FSMContext, bot: Bot):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('❌ Отменено.',reply_markup=kb.main)
        return   
    user_id = message.from_user.id
    username = f'@{message.from_user.username}' if message.from_user.username else 'без username'
    full_name = message.from_user.full_name    
    admin_text = f'📨 <b>ЗАЯВКА НА УДАЛЕНИЕ</b>\n👤 От: {full_name}\n🔗 {username} | ID: <code>{user_id}</code>\n{message.text}'    
    await bot.send_message(chat_id=-1003627692695,message_thread_id=237,text=admin_text,parse_mode='HTML')
    await message.answer('✅ <b>Заявка отправлена!</b>',reply_markup=kb.main,parse_mode='HTML')
    await state.clear()

@user.message(F.text == 'Назад в меню')
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('👋 Привет! Мы - "Узнай за УИ"!',reply_markup=kb.main)

@user.message(PostStates.waiting_for_post)
async def process_any_post(message: Message, state: FSMContext, bot: Bot):
    from app import post_user_map
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('👋 Привет! Мы - "Узнай за УИ"!',reply_markup=kb.main)
        return
    user_id = message.from_user.id
    if message.text:
        new_text = message.text + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_message(chat_id=-1003627692695, message_thread_id=232, text=new_text, parse_mode='HTML')
        post_user_map[post_msg.message_id] = user_id
    elif message.photo:
        caption = message.caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>" if message.caption else "<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_photo(chat_id=-1003627692695, message_thread_id=232, photo=message.photo[-1].file_id, caption=caption, parse_mode='HTML')
        post_user_map[post_msg.message_id] = user_id    
    elif message.video:
        caption = message.caption + "\n\n<a href='https://t.me/yznay138'>Узнай за УИ</a>" if message.caption else "<a href='https://t.me/yznay138'>Узнай за УИ</a>"
        post_msg = await bot.send_video(chat_id=-1003627692695, message_thread_id=232, video=message.video.file_id, caption=caption, parse_mode='HTML')
        post_user_map[post_msg.message_id] = user_id
    else:
        post_msg = await bot.copy_message(chat_id=-1003627692695, from_chat_id=message.chat.id, message_id=message.message_id, message_thread_id=232)
        post_user_map[post_msg.message_id] = user_id
    await message.answer('✅ <b>Пост отправлен на модерацию!</b>', reply_markup=kb.main, parse_mode='HTML')
    await state.clear()

@user.message(F.chat.id == -1003607675754) 
async def on_group_message(message: Message, bot: Bot):
    if message.sender_chat and message.sender_chat.id == -1003550629921: 
        await bot.send_message(chat_id=-1003607675754,reply_to_message_id=message.message_id,text='📨 @UznaiZaUI_bot',parse_mode='HTML')
