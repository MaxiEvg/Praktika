import pytest
from unittest.mock import MagicMock, patch
import telebot
from bot_main import create_main_menu, get_welcome_message

@pytest.fixture
def mock_bot():
    with patch('telebot.TeleBot') as mock:
        bot = mock.return_value
        yield bot

@pytest.fixture
def mock_message():
    message = MagicMock()
    message.chat.id = 123456
    message.from_user.id = 123456
    return message

@pytest.fixture
def mock_call():
    call = MagicMock()
    call.message.chat.id = 123456
    call.message.message_id = 1
    call.from_user.id = 123456
    return call

def test_create_main_menu():
    """Test main menu creation"""
    markup = create_main_menu()
    assert markup is not None
    assert len(markup.keyboard) == 4
    assert markup.keyboard[0][0].text == 'Информация о компании'
    assert markup.keyboard[0][0].callback_data == 'company_info'

def test_get_welcome_message():
    """Test welcome message format"""
    message = get_welcome_message()
    assert isinstance(message, str)
    assert 'Добр пожаловать' in message
    assert 'бот-помощник по адаптации' in message

def test_start_command(mock_bot, mock_message):
    """Test /start command handler"""
    with patch('bot_main.logger') as mock_logger:
        # Call the start handler
        from bot_main import start
        start(mock_message)
        
        # Verify logging
        mock_logger.info.assert_called_once()
        
        # Verify message was sent
        mock_bot.send_message.assert_called_once()
        args, kwargs = mock_bot.send_message.call_args
        assert kwargs['chat_id'] == mock_message.chat.id
        assert kwargs['reply_markup'] is not None

def test_back_button(mock_bot, mock_call):
    """Test back button functionality"""
    with patch('bot_main.logger') as mock_logger:
        # Set up the callback data
        mock_call.data = 'back_to_main'
        
        # Call the callback handler
        from bot_main import callback_handler
        callback_handler(mock_call)
        
        # Verify logging
        mock_logger.info.assert_called_once()
        
        # Verify message was edited
        mock_bot.edit_message_text.assert_called_once()
        args, kwargs = mock_bot.edit_message_text.call_args
        assert kwargs['chat_id'] == mock_call.message.chat.id
        assert kwargs['message_id'] == mock_call.message.message_id
        assert kwargs['reply_markup'] is not None

def test_company_info_button(mock_bot, mock_call):
    """Test company info button functionality"""
    with patch('bot_main.logger') as mock_logger:
        # Set up the callback data
        mock_call.data = 'company_info'
        
        # Call the callback handler
        from bot_main import callback_handler
        callback_handler(mock_call)
        
        # Verify logging
        mock_logger.info.assert_called_once()
        
        # Verify message was edited
        mock_bot.edit_message_text.assert_called_once()
        args, kwargs = mock_bot.edit_message_text.call_args
        assert kwargs['chat_id'] == mock_call.message.chat.id
        assert kwargs['message_id'] == mock_call.message.message_id
        assert kwargs['reply_markup'] is not None 