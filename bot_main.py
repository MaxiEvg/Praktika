import telebot
from telebot import types
import logging
from config import Config
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT,
    filename=Config.LOG_FILE
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(Config.BOT_TOKEN)

# Button templates for different sections
BUTTON_TEMPLATES = {
    'main_menu': [
        ('Информация о компании', 'company_info'),
        ('Материалы по стажировкам', 'internship'),
        ('План адаптации', 'adaptation'),
        ('Написать HR', 'hr')
    ],
    'company_info': [
        ('Прочитать статью', 'read_article'),
        ('Посмотреть видео', 'watch_video'),
        ('Пройти тест', 'take_test'),
        ('Назад', 'back_to_main')
    ],
    'internship': [
        ('Программа стажировки', 'internship_program'),
        ('Расписание', 'internship_schedule'),
        ('Наставники', 'mentors'),
        ('Документы', 'internship_docs'),
        ('Назад', 'back_to_main')
    ],
    'adaptation': [
        ('Мой план', 'my_plan'),
        ('Прогресс', 'progress'),
        ('Задачи', 'tasks'),
        ('Обратная связь', 'feedback'),
        ('Назад', 'back_to_main')
    ],
    'hr': [
        ('Задать вопрос', 'ask_question'),
        ('Записаться на встречу', 'schedule_meeting'),
        ('Отправить документы', 'submit_docs'),
        ('Назад', 'back_to_main')
    ],
    'test': [
        ('Начать тест', 'start_test'),
        ('Продолжить тест', 'continue_test'),
        ('Результаты', 'test_results'),
        ('Назад', 'back_to_main')
    ]
}

def create_menu_markup(menu_type: str) -> types.InlineKeyboardMarkup:
    """Create menu markup based on button template"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = BUTTON_TEMPLATES.get(menu_type, BUTTON_TEMPLATES['main_menu'])
    markup.add(*[types.InlineKeyboardButton(text=text, callback_data=data) 
                 for text, data in buttons])
    return markup

def get_welcome_message() -> str:
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

def get_section_message(section: str) -> str:
    """Get formatted message for specific section"""
    messages = {
        'company_info': """📅 Знакомство с компанией

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
        'internship': """📚 Материалы по стажировке

Здесь ты найдешь всю необходимую
информацию о программе стажировки,
расписании и наставниках.

Выбери интересующий раздел:""",
        'adaptation': """📋 План адаптации

Здесь ты можешь отслеживать свой
прогресс, просматривать задачи и
отправлять обратную связь.

Выбери действие:""",
        'hr': """👥 HR поддержка

Здесь ты можешь задать вопросы HR,
записаться на встречу или отправить
необходимые документы.

Выбери действие:"""
    }
    return messages.get(section, get_welcome_message())

@bot.message_handler(commands=['start'])
def start(message):
    """Handle /start command with logging"""
    try:
        logger.info(f"User {message.from_user.id} started the bot")
        markup = create_menu_markup('main_menu')
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
            markup = create_menu_markup('main_menu')
            bot.edit_message_text(
                get_welcome_message(),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        elif call.data in BUTTON_TEMPLATES:
            logger.info(f"User {call.from_user.id} accessed {call.data}")
            markup = create_menu_markup(call.data)
            bot.edit_message_text(
                get_section_message(call.data),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        # Add specific handlers for other actions here
        elif call.data == 'start_test':
            # TODO: Implement test start logic
            pass
        elif call.data == 'ask_question':
            # TODO: Implement question asking logic
            pass
        elif call.data == 'schedule_meeting':
            # TODO: Implement meeting scheduling logic
            pass
        elif call.data == 'submit_docs':
            # TODO: Implement document submission logic
            pass
        
    except Exception as e:
        logger.error(f"Error in callback handler: {str(e)}")
        bot.answer_callback_query(call.id, "Произошла ошибка. Пожалуйста, попробуйте позже.")

if __name__ == '__main__':
    logger.info("Bot started")
    bot.infinity_polling()