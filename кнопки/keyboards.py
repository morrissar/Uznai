from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пользовательское соглашение')],
    [KeyboardButton(text='Предложить пост')],
    [KeyboardButton(text='Удалить пост')],
    [KeyboardButton(text='Контакты руководства')]
], resize_keyboard=True,
    input_field_placeholder='Выберите действие')

after_soglash = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text='Назад в меню')]
    ], resize_keyboard=True, input_field_placeholder='Читайте внимательно')

after_predloji = ReplyKeyboardMarkup( 
    keyboard=[
    [KeyboardButton(text='Назад в меню')]  
    ], resize_keyboard=True, input_field_placeholder='Ждем ваши посты')

after_udali = ReplyKeyboardMarkup(  
    keyboard=[
    [KeyboardButton(text='Платное удаление'), KeyboardButton(text='Бесплатное удаление')],
    [KeyboardButton(text='Назад в меню')]
    ], resize_keyboard=True, input_field_placeholder='Подавайте заявку')