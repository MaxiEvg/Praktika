import telebot
from telebot import types
import logging
from config import Config
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import requests
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API errors"""
    pass

class DatabaseService:
    """Service for handling database operations via API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make API request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}")
    
    def get_materials(self, category: Optional[str] = None) -> List[Dict]:
        """Get materials from database"""
        endpoint = '/content'
        if category:
            endpoint += f'?category={category}'
        return self._make_request('GET', endpoint)
    
    def get_lectures(self) -> List[Dict]:
        """Get all lectures from database"""
        return self._make_request('GET', '/content?type=lecture')
    
    def get_tests(self) -> List[Dict]:
        """Get all tests from database"""
        return self._make_request('GET', '/content?type=test')
    
    def get_adaptation_plan(self, user_id: int) -> Dict:
        """Get user's adaptation plan"""
        return self._make_request('GET', f'/adaptation/plan/{user_id}')
    
    def get_progress(self, user_id: int) -> Dict:
        """Get user's progress"""
        return self._make_request('GET', f'/adaptation/progress/{user_id}')
    
    def save_feedback(self, user_id: int, feedback_text: str) -> None:
        """Save user feedback"""
        self._make_request('POST', '/adaptation/feedback', {
            'user_id': user_id,
            'feedback_text': feedback_text,
            'created_at': datetime.now().isoformat()
        })
    
    def save_question(self, user_id: int, question_text: str) -> None:
        """Save user question"""
        self._make_request('POST', '/adaptation/questions', {
            'user_id': user_id,
            'question_text': question_text,
            'created_at': datetime.now().isoformat()
        })
    
    def save_document(self, user_id: int, file_id: str, file_name: str) -> None:
        """Save document info"""
        self._make_request('POST', '/adaptation/documents', {
            'user_id': user_id,
            'file_id': file_id,
            'file_name': file_name,
            'uploaded_at': datetime.now().isoformat()
        })
    
    def get_test_questions(self, test_id: int) -> List[Dict]:
        """Get test questions"""
        return self._make_request('GET', f'/content/{test_id}/questions')
    
    def save_test_result(self, user_id: int, test_id: int, score: int, total: int) -> None:
        """Save test result"""
        self._make_request('POST', '/adaptation/test-results', {
            'user_id': user_id,
            'test_id': test_id,
            'score': score,
            'total_questions': total,
            'completion_time': datetime.now().isoformat()
        })

# Initialize services
db_service = DatabaseService(Config.API_BASE_URL)
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
        ('Назад', 'back_to_main')
    ],
    'internship': [
        ('Прочитать статью', 'read_article'),   # ('Программа стажировки', 'internship_program'),
        ('Посмотреть видео', 'watch_video'),    # ('Расписание', 'internship_schedule'),
        ('Пройти тест', 'take_test'),           # ('Документы', 'internship_docs'),    
        ('Назад', 'back_to_main')
    ],
    'adaptation': [
        ('Мой план', 'my_plan'),
        ('Прогресс', 'progress'),
        ('Обратная связь', 'feedback'),
        ('Назад', 'back_to_main')
    ],
    'hr': [
        ('Задать вопрос', 'ask_question'),
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

def get_section_message(section: str, user_id: int) -> str:
    """Get formatted message for specific section with dynamic content"""
    try:
        if section == 'internship':
            materials = db_service.get_materials(category='internship')
            lectures = db_service.get_lectures()
            tests = db_service.get_tests()
            
            message = """📚 Материалы по стажировке

Доступные материалы:
"""
            if materials:
                message += "\n📖 Материалы:\n"
                for material in materials:
                    message += f"- {material['title']}\n"
                    if material.get('description'):
                        message += f"  {material['description']}\n"
            
            if lectures:
                message += "\n🎥 Лекции:\n"
                for lecture in lectures:
                    message += f"- {lecture['title']}\n"
                    if lecture.get('description'):
                        message += f"  {lecture['description']}\n"
            
            if tests:
                message += "\n📝 Тесты:\n"
                for test in tests:
                    message += f"- {test['title']}\n"
                    if test.get('description'):
                        message += f"  {test['description']}\n"
            
            message += "\nВыбери интересующий раздел:"
            return message
            
        elif section == 'company_info':
            materials = db_service.get_materials(category='company_info')
            message = """📅 Знакомство с компанией

Доступные материалы:
"""
            if materials:
                for material in materials:
                    message += f"- {material['title']}\n"
                    if material.get('description'):
                        message += f"  {material['description']}\n"
            
            message += "\nПосле изучения пройди тест"
            return message
            
        elif section == 'adaptation':
            plan = db_service.get_adaptation_plan(user_id)
            progress = db_service.get_progress(user_id)
            
            message = """📋 План адаптации

Ваш план:
"""
            if plan:
                for step in plan.get('steps', []):
                    message += f"- {step['title']}\n"
                    if step.get('description'):
                        message += f"  {step['description']}\n"
            
            if progress:
                message += f"\nПрогресс: {progress['completed_steps']}/{progress['total_steps']} шагов"
            
            return message
            
        else:
            return get_welcome_message()
            
    except APIError as e:
        logger.error(f"Error getting section content: {str(e)}")
        return "Произошла ошибка при загрузке материалов. Пожалуйста, попробуйте позже."

def create_back_button_markup() -> types.InlineKeyboardMarkup:
    """Create markup with back to main menu button"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Вернуться в главное меню", callback_data='back_to_main'))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    """Handle /start command with logging"""
    try:
        logger.info(f"User {message.from_user.id} ({message.from_user.username}) started the bot")
        logger.info(f"User details: first_name={message.from_user.first_name}, last_name={message.from_user.last_name}")
        markup = create_menu_markup('main_menu')
        bot.send_message(message.chat.id, get_welcome_message(), reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}")
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте позже.", 
                    reply_markup=create_back_button_markup())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Handle all callback queries with improved error handling and logging"""
    try:
        logger.info(f"User {call.from_user.id} ({call.from_user.username}) pressed button: {call.data}")
        
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
            logger.info(f"User {call.from_user.id} accessed section: {call.data}")
            markup = create_menu_markup(call.data)
            try:
                message = get_section_message(call.data, call.from_user.id)
                bot.edit_message_text(
                    message,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
            except APIError as e:
                logger.error(f"Error getting section content: {str(e)}")
                bot.edit_message_text(
                    "Произошла ошибка при загрузке материалов",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=create_back_button_markup()
                )
        elif call.data == 'start_test':
            logger.info(f"User {call.from_user.id} started test")
            try:
                questions = db_service.get_test_questions()
                
                # Store test state
                test_state = {
                    'questions': questions,
                    'current_question': 0,
                    'answers': [],
                    'start_time': datetime.now().isoformat()
                }
                
                # Send first question
                question = questions[0]
                markup = types.InlineKeyboardMarkup()
                for option in question['options']:
                    markup.add(types.InlineKeyboardButton(
                        text=option['text'],
                        callback_data=f"answer_{option['id']}"
                    ))
                
                bot.edit_message_text(
                    f"Вопрос 1/5:\n{question['text']}",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                
                # Store test state in user data
                bot.set_state(call.from_user.id, json.dumps(test_state))
                
            except APIError as e:
                logger.error(f"API error starting test: {str(e)}")
                bot.edit_message_text(
                    "Произошла ошибка при загрузке теста",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=create_back_button_markup()
                )
                
        elif call.data == 'ask_question':
            logger.info(f"User {call.from_user.id} requested to ask a question")
            bot.edit_message_text(
                "Пожалуйста, напишите ваш вопрос:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=create_back_button_markup()
            )
            bot.register_next_step_handler(call.message, process_question)
            
        elif call.data == 'submit_docs':
            logger.info(f"User {call.from_user.id} requested to submit documents")
            bot.edit_message_text(
                "Пожалуйста, отправьте документы:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=create_back_button_markup()
            )
            bot.register_next_step_handler(call.message, process_documents)
            
        elif call.data.startswith('answer_'):
            logger.info(f"User {call.from_user.id} answered test question: {call.data}")
            answer_id = int(call.data.split('_')[1])
            state = json.loads(bot.get_state(call.from_user.id))
            
            # Store answer
            state['answers'].append(answer_id)
            state['current_question'] += 1
            
            if state['current_question'] < len(state['questions']):
                # Show next question
                question = state['questions'][state['current_question']]
                markup = types.InlineKeyboardMarkup()
                for option in question['options']:
                    markup.add(types.InlineKeyboardButton(
                        text=option['text'],
                        callback_data=f"answer_{option['id']}"
                    ))
                
                bot.edit_message_text(
                    f"Вопрос {state['current_question'] + 1}/5:\n{question['text']}",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=markup
                )
                
                bot.set_state(call.from_user.id, json.dumps(state))
            else:
                # Test completed
                try:
                    # Calculate score
                    score = sum(1 for i, answer in enumerate(state['answers']) 
                              if answer == state['questions'][i]['correct_answer'])
                    
                    # Save results via API
                    db_service.save_test_result(
                        user_id=call.from_user.id,
                        test_id=state['questions'][0]['test_id'],
                        score=score,
                        total=len(state['questions'])
                    )
                    
                    # Show results
                    bot.edit_message_text(
                        f"Тест завершен!\nВаш результат: {score}/{len(state['questions'])}",
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=create_back_button_markup()
                    )
                    
                except APIError as e:
                    logger.error(f"API error saving test results: {str(e)}")
                    bot.edit_message_text(
                        "Произошла ошибка при сохранении результатов",
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=create_back_button_markup()
                    )
                finally:
                    bot.delete_state(call.from_user.id)
        
    except Exception as e:
        logger.error(f"Error in callback handler for user {call.from_user.id}: {str(e)}")
        bot.edit_message_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=create_back_button_markup()
        )

def process_question(message):
    """Process user question and save via API"""
    logger.info(f"User {message.from_user.id} submitted question: {message.text[:100]}...")
    try:
        db_service.save_question(message.from_user.id, message.text)
        bot.reply_to(message, "Ваш вопрос отправлен HR. Ожидайте ответа.", 
                    reply_markup=create_back_button_markup())
    except APIError as e:
        logger.error(f"API error saving question: {str(e)}")
        bot.reply_to(message, "Произошла ошибка при отправке вопроса",
                    reply_markup=create_back_button_markup())

def process_documents(message):
    """Process uploaded documents via API"""
    if message.document:
        logger.info(f"User {message.from_user.id} uploaded document: {message.document.file_name}")
        try:
            db_service.save_document(
                user_id=message.from_user.id,
                file_id=message.document.file_id,
                file_name=message.document.file_name
            )
            bot.reply_to(message, "Документ успешно загружен.",
                        reply_markup=create_back_button_markup())
        except APIError as e:
            logger.error(f"API error saving document: {str(e)}")
            bot.reply_to(message, "Произошла ошибка при загрузке документа",
                        reply_markup=create_back_button_markup())
    else:
        logger.warning(f"User {message.from_user.id} tried to submit non-document content")
        bot.reply_to(message, "Пожалуйста, отправьте документ.",
                    reply_markup=create_back_button_markup())

@bot.message_handler(commands=['clear'])
def clear_chat(message):
    """Clear all bot messages and restart conversation"""
    try:
        logger.info(f"User {message.from_user.id} requested chat clear")
        
        # Get all messages in chat
        chat_id = message.chat.id
        messages = bot.get_updates()
        
        # Delete all bot messages
        for msg in messages:
            if msg.message and msg.message.chat.id == chat_id:
                try:
                    bot.delete_message(chat_id, msg.message.message_id)
                except Exception as e:
                    logger.warning(f"Could not delete message {msg.message.message_id}: {str(e)}")
        
        # Send new start message
        markup = create_menu_markup('main_menu')
        bot.send_message(chat_id, get_welcome_message(), reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error in clear handler: {str(e)}")
        bot.reply_to(message, "Произошла ошибка при очистке чата",
                    reply_markup=create_back_button_markup())

if __name__ == '__main__':
    logger.info("Bot started")
    bot.infinity_polling()