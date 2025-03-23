import telebot
from telebot import types
import logging
from config import Config

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT,
    filename=Config.LOG_FILE
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(Config.BOT_TOKEN)

def create_main_menu():
    """Create main menu markup with standard buttons"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        ('Информация о компании', 'company_info'),
        ('Материалы по стажировкам', 'internship'),
        ('План адаптации', 'adaptation'),
        ('Написать HR', 'hr')
    ]
    markup.add(*[types.InlineKeyboardButton(text=text, callback_data=data) 
                 for text, data in buttons])
    return markup

def get_welcome_message():
    """Get formatted welcome message"""
    return """👋 Добр пожаловать в компанию!
Я — бот-помощник по адаптации. Здесь ты
найдёшь важную информацию о
компании, материалы для обучения
и свой план

🔻 Давай начнем! Выбери, с чего
хочешь начать:

Если у тебя возникнут вопросы,
всегда можешь к HR. 🚀"""

@bot.message_handler(commands=['start'])
def start(message):
    """Handle /start command with logging"""
    try:
        logger.info(f"User {message.from_user.id} started the bot")
        markup = create_main_menu()
        bot.send_message(message.chat.id, get_welcome_message(), reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}")
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте позже.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Handle all callback queries with improved error handling and logging"""
    try:
        if call.data == 'back_to_main':
            logger.info(f"User {call.from_user.id} returned to main menu")
            markup = create_main_menu()
            bot.edit_message_text(
                get_welcome_message(),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        elif call.data == 'company_info':
            logger.info(f"User {call.from_user.id} accessed company info")
            markup = types.InlineKeyboardMarkup(row_width=1)
            buttons = [
                ('Прочитать статью', 'read_article'),
                ('Посмотреть видео', 'watch_video'),
                ('Пройти тест', 'take_test'),
                ('Назад', 'back_to_main')
            ]
            markup.add(*[types.InlineKeyboardButton(text=text, callback_data=data) 
                        for text, data in buttons])
            
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
        # Add other handlers here...
        
    except Exception as e:
        logger.error(f"Error in callback handler: {str(e)}")
        bot.answer_callback_query(call.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

if __name__ == '__main__':
    logger.info("Bot started")
    bot.infinity_polling()