import telebot
from telebot import types

bot = telebot.TeleBot('7533441974:AAGU815eL1cHblfYeaURKFus7GCCcjCiwa0')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='Информация о компании', callback_data='company_info')
    btn2 = types.InlineKeyboardButton(text='Материалы по стажировкам', callback_data='internship')
    btn3 = types.InlineKeyboardButton(text='План адаптации', callback_data='adaptation')
    btn4 = types.InlineKeyboardButton(text='Написать HR', callback_data='hr')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, """👋 Добр пожаловать в компанию!
    Я — бот-помощник по адаптации. Здесь ты
    найдёшь важную информацию о
    компании, материалы для обучения
    и свой план

    🔻 Давай начнем! Выбери, с чего
    хочешь начать:

    Если у тебя возникнут вопросы,
    всегда можешь к HR. 🚀""", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'company_info':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Прочитать статью', callback_data='read_article')
        btn2 = types.InlineKeyboardButton(text='Посмотреть видео', callback_data='watch_video')
        btn3 = types.InlineKeyboardButton(text='Пройти тест', callback_data='take_test')
        btn4 = types.InlineKeyboardButton(text='Назад', callback_data='back_to_main')
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.edit_message_text(
            """📅 Знакомство с компанией

🗒 Тебе предстоит: узнать о нас
✅ И [Краткое описание задач этапа]

📌 Материалы для изучения:
📖 История компании
📹 Приветствие от основателя
🔍 После изучения пройди тест

⚡️ Не затягивай! Следующий этап
станет доступен после завершения
текущего. Если возникли вопросы,
пиши HR. 🚀""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    elif call.data == 'back_to_main':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Информация о компании', callback_data='company_info')
        btn2 = types.InlineKeyboardButton(text='Материалы по стажировкам', callback_data='internship')
        btn3 = types.InlineKeyboardButton(text='План адаптации', callback_data='adaptation')
        btn4 = types.InlineKeyboardButton(text='Написать HR', callback_data='hr')
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.edit_message_text(
            """👋 Добр пожаловать в компанию!
    Я — бот-помощник по адаптации. Здесь ты
    найдёшь важную информацию о
    компании, материалы для обучения
    и свой план

    🔻 Давай начнем! Выбери, с чего
    хочешь начать:

    Если у тебя возникнут вопросы,
    всегда можешь к HR. 🚀""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

bot.infinity_polling()